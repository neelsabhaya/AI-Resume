"""api/schemas.py

Pydantic request/response models for the API.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ── Request Schemas ────────────────────────────────────────────────────────────

class JobDescriptionRequest(BaseModel):
    title: str = Field(default="Untitled Position", description="Job title")
    description: str = Field(..., description="Full job description text")


# ── Response Schemas ───────────────────────────────────────────────────────────

class ScoreBreakdown(BaseModel):
    skills_score: float
    experience_score: float
    education_score: float
    text_similarity_score: float


class FraudInfo(BaseModel):
    is_suspicious: bool
    risk_level: str
    reasons: List[str]


class CandidateResult(BaseModel):
    candidate_id: int
    filename: str
    name: str
    rank: int
    final_score: float
    fit_percentage: float
    grade: str
    experience_years: float
    education: str
    skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    breakdown: ScoreBreakdown
    fraud: FraudInfo
    feedback: List[str]


class JobUploadResponse(BaseModel):
    job_id: int
    title: str
    message: str
    required_skills: List[str]
    required_experience_years: float
    required_education: str


class AnalysisResponse(BaseModel):
    job_id: int
    job_title: str
    total_candidates: int
    shortlisted_count: int
    candidates: List[CandidateResult]
    processing_time_seconds: float


class CompareResponse(BaseModel):
    job_id: int
    candidates: List[CandidateResult]


class FeedbackResponse(BaseModel):
    candidate_id: int
    filename: str
    final_score: float
    feedback: List[str]
    missing_skills: List[str]
