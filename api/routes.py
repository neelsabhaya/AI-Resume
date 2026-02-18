"""api/routes.py

FastAPI router with all endpoints for the Resume Screening System.
"""
import os
import time
import logging
import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.connection import get_db
from models.db_models import Job, Candidate, Score
from parsers.resume_parser import parse_resume
from nlp_engine.preprocessor import preprocess
from services.extractor import extract_features
from services.matcher import match_resume_to_jd
from scoring.scorer import score_candidate, rank_candidates, detect_fraud, generate_feedback
from api.schemas import (
    JobDescriptionRequest, JobUploadResponse, AnalysisResponse,
    CandidateResult, ScoreBreakdown, FraudInfo, CompareResponse, FeedbackResponse
)
from config import UPLOAD_DIR
from utils.helpers import validate_file

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Resume Screening"])


def _extract_candidate_name(text: str, filename: str) -> str:
    """Try to extract candidate name from first lines of resume text."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if lines:
        first_line = lines[0]
        # If first line looks like a name (2-4 words, no special chars)
        words = first_line.split()
        if 1 < len(words) <= 4 and all(w.isalpha() for w in words):
            return first_line
    # Fallback: use filename without extension
    return Path(filename).stem.replace("_", " ").replace("-", " ").title()


def _build_candidate_result(candidate: Candidate, score: Score, rank: int) -> CandidateResult:
    """Build a CandidateResult response object from DB models."""
    return CandidateResult(
        candidate_id=candidate.id,
        filename=candidate.filename,
        name=candidate.name,
        rank=rank,
        final_score=score.final_score,
        fit_percentage=score.fit_percentage,
        grade=score.grade,
        experience_years=candidate.experience_years,
        education=candidate.education,
        skills=candidate.skills or [],
        matched_skills=score.matched_skills or [],
        missing_skills=score.missing_skills or [],
        breakdown=ScoreBreakdown(
            skills_score=score.skills_score,
            experience_score=score.experience_score,
            education_score=score.education_score,
            text_similarity_score=score.text_similarity_score,
        ),
        fraud=FraudInfo(
            is_suspicious=candidate.is_suspicious,
            risk_level=candidate.fraud_risk_level,
            reasons=candidate.fraud_reasons or [],
        ),
        feedback=score.feedback or [],
    )


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/upload-jd", response_model=JobUploadResponse, summary="Upload Job Description")
async def upload_job_description(
    title: str = Form(default="Untitled Position"),
    description: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a job description. Extracts required skills, experience, and education.
    Returns a job_id to use for subsequent resume uploads.
    """
    if len(description.strip()) < 20:
        raise HTTPException(status_code=400, detail="Job description is too short.")

    # Extract JD features
    jd_features = extract_features(description)

    # Save to DB
    job = Job(
        title=title,
        description=description,
        required_skills=jd_features["skills"],
        required_experience_years=jd_features["experience_years"],
        required_education=jd_features["education"],
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)

    return JobUploadResponse(
        job_id=job.id,
        title=job.title,
        message=f"Job description uploaded successfully. Found {len(jd_features['skills'])} required skills.",
        required_skills=jd_features["skills"],
        required_experience_years=jd_features["experience_years"],
        required_education=jd_features["education"],
    )


@router.post("/upload-resumes/{job_id}", response_model=AnalysisResponse, summary="Upload & Analyze Resumes")
async def upload_and_analyze_resumes(
    job_id: int,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload multiple resume files (PDF/DOCX/TXT) for a given job.
    Parses, analyzes, scores, and ranks all candidates.
    Returns ranked results immediately.
    """
    start_time = time.time()

    # Fetch job
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with id={job_id} not found.")

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    jd_features = {
        "skills": job.required_skills or [],
        "experience_years": job.required_experience_years or 3.0,
        "education": job.required_education or "unknown",
        "raw_text": job.description,
    }

    # Process each resume
    job_upload_dir = UPLOAD_DIR / str(job_id)
    job_upload_dir.mkdir(parents=True, exist_ok=True)

    scored_candidates = []
    file_issues: List[str] = []

    for upload_file in files:
        filename = upload_file.filename or "resume.pdf"
        ext = Path(filename).suffix.lower()

        if ext not in (".pdf", ".docx", ".doc", ".txt"):
            logger.warning(f"Skipping unsupported file: {filename}")
            file_issues.append(f"{filename}: unsupported file type '{ext}'")
            continue

        # Validate file
        is_valid, error_msg = validate_file(filename, upload_file.size or 0)
        if not is_valid:
            logger.warning(f"Skipping file {filename}: {error_msg}")
            file_issues.append(f"{filename}: {error_msg}")
            continue

        # Save file
        file_path = job_upload_dir / filename
        try:
            with open(file_path, "wb") as f:
                shutil.copyfileobj(upload_file.file, f)
        except Exception as e:
            logger.error(f"Failed to save {filename}: {e}")
            file_issues.append(f"{filename}: failed to save file ({e})")
            continue

        # Parse
        raw_text = parse_resume(str(file_path))
        if not raw_text:
            logger.warning(f"No text extracted from {filename}")
            file_issues.append(
                f"{filename}: no text extracted (likely scanned/image-only PDF or unsupported content)"
            )
            continue

        # Extract features
        resume_features = extract_features(raw_text)

        # Fraud detection
        fraud_result = detect_fraud(raw_text)

        # Match
        match_result = match_resume_to_jd(jd_features, resume_features)

        # Score
        score_result = score_candidate(jd_features, resume_features, match_result)

        # Feedback
        feedback = generate_feedback(jd_features, resume_features, score_result)

        # Extract name
        candidate_name = _extract_candidate_name(raw_text, filename)

        # Save candidate to DB
        candidate = Candidate(
            job_id=job_id,
            filename=filename,
            name=candidate_name,
            raw_text=raw_text[:5000],  # Store truncated text
            skills=resume_features["skills"],
            experience_years=resume_features["experience_years"],
            education=resume_features["education"],
            is_suspicious=fraud_result["is_suspicious"],
            fraud_risk_level=fraud_result["risk_level"],
            fraud_reasons=fraud_result["reasons"],
        )
        db.add(candidate)
        await db.flush()
        await db.refresh(candidate)

        # Save score to DB
        breakdown = score_result["breakdown"]
        score_obj = Score(
            candidate_id=candidate.id,
            final_score=score_result["final_score"],
            fit_percentage=score_result["fit_percentage"],
            grade=score_result["grade"],
            rank=0,  # Will be updated after ranking
            skills_score=breakdown["skills_score"],
            experience_score=breakdown["experience_score"],
            education_score=breakdown["education_score"],
            text_similarity_score=breakdown["text_similarity_score"],
            matched_skills=score_result["matched_skills"],
            missing_skills=score_result["missing_skills"],
            feedback=feedback,
        )
        db.add(score_obj)
        await db.flush()
        await db.refresh(score_obj)

        scored_candidates.append({
            "candidate": candidate,
            "score": score_obj,
            "final_score": score_result["final_score"],
        })

    if not scored_candidates:
        detail_msg = "No valid resumes could be processed."
        if file_issues:
            detail_msg += " Issues: " + "; ".join(file_issues)
        raise HTTPException(status_code=422, detail=detail_msg)

    # Rank candidates
    ranked = rank_candidates(scored_candidates)

    # Update ranks in DB
    for item in ranked:
        item["score"].rank = item["rank"]

    await db.commit()

    # Build response
    candidate_results = [
        _build_candidate_result(item["candidate"], item["score"], item["rank"])
        for item in ranked
    ]

    shortlisted = [c for c in candidate_results if c.final_score >= 60]
    elapsed = round(time.time() - start_time, 2)

    return AnalysisResponse(
        job_id=job_id,
        job_title=job.title,
        total_candidates=len(candidate_results),
        shortlisted_count=len(shortlisted),
        candidates=candidate_results,
        processing_time_seconds=elapsed,
    )


@router.get("/results/{job_id}", response_model=AnalysisResponse, summary="Get Ranked Results")
async def get_results(job_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve previously computed ranked results for a job."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with id={job_id} not found.")

    candidates_result = await db.execute(
        select(Candidate).where(Candidate.job_id == job_id)
    )
    candidates = candidates_result.scalars().all()

    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found for this job.")

    candidate_results = []
    for candidate in candidates:
        score_result = await db.execute(
            select(Score).where(Score.candidate_id == candidate.id)
        )
        score = score_result.scalar_one_or_none()
        if score:
            candidate_results.append(
                _build_candidate_result(candidate, score, score.rank)
            )

    candidate_results.sort(key=lambda c: c.rank)
    shortlisted = [c for c in candidate_results if c.final_score >= 60]

    return AnalysisResponse(
        job_id=job_id,
        job_title=job.title,
        total_candidates=len(candidate_results),
        shortlisted_count=len(shortlisted),
        candidates=candidate_results,
        processing_time_seconds=0.0,
    )


@router.get("/compare", response_model=CompareResponse, summary="Compare Candidates")
async def compare_candidates(
    job_id: int,
    candidate_ids: str,  # comma-separated IDs e.g. "1,2,3"
    db: AsyncSession = Depends(get_db),
):
    """Compare specific candidates side-by-side."""
    ids = [int(i.strip()) for i in candidate_ids.split(",") if i.strip().isdigit()]
    if not ids:
        raise HTTPException(status_code=400, detail="Provide valid candidate_ids (comma-separated).")

    candidate_results = []
    for cid in ids:
        c_result = await db.execute(select(Candidate).where(Candidate.id == cid, Candidate.job_id == job_id))
        candidate = c_result.scalar_one_or_none()
        if candidate:
            s_result = await db.execute(select(Score).where(Score.candidate_id == cid))
            score = s_result.scalar_one_or_none()
            if score:
                candidate_results.append(_build_candidate_result(candidate, score, score.rank))

    return CompareResponse(job_id=job_id, candidates=candidate_results)


@router.get("/feedback/{candidate_id}", response_model=FeedbackResponse, summary="Get AI Feedback")
async def get_feedback(candidate_id: int, db: AsyncSession = Depends(get_db)):
    """Get AI-generated improvement feedback for a specific candidate."""
    c_result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = c_result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found.")

    s_result = await db.execute(select(Score).where(Score.candidate_id == candidate_id))
    score = s_result.scalar_one_or_none()
    if not score:
        raise HTTPException(status_code=404, detail="Score not found for this candidate.")

    return FeedbackResponse(
        candidate_id=candidate_id,
        filename=candidate.filename,
        final_score=score.final_score,
        feedback=score.feedback or [],
        missing_skills=score.missing_skills or [],
    )


@router.get("/jobs", summary="List All Jobs")
async def list_jobs(db: AsyncSession = Depends(get_db)):
    """List all uploaded job descriptions."""
    result = await db.execute(select(Job))
    jobs = result.scalars().all()
    return [
        {"id": j.id, "title": j.title, "created_at": j.created_at.isoformat()}
        for j in jobs
    ]


@router.delete("/jobs/{job_id}", summary="Delete a Job")
async def delete_job(job_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a job and all its candidates/scores."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")
    await db.delete(job)
    return {"message": f"Job {job_id} deleted successfully."}
