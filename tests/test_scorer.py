"""tests/test_scorer.py"""
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_score_candidate_returns_valid_range():
    """Test that final score is between 0 and 100."""
    from scoring.scorer import score_candidate
    jd_features = {"skills": ["python", "fastapi"], "experience_years": 3.0, "education": "bachelor"}
    resume_features = {"skills": ["python", "fastapi", "docker"], "experience_years": 4.0, "education": "bachelor"}
    match_result = {
        "skill_overlap": 1.0,
        "blended_text_score": 0.8,
        "matched_skills": ["python", "fastapi"],
        "missing_skills": [],
    }
    result = score_candidate(jd_features, resume_features, match_result)
    assert 0 <= result["final_score"] <= 100
    assert result["grade"] in ["A", "B", "C", "D", "F"]


def test_rank_candidates_sorts_descending():
    """Test that rank_candidates sorts by score descending."""
    from scoring.scorer import rank_candidates
    candidates = [
        {"final_score": 45.0},
        {"final_score": 82.0},
        {"final_score": 63.0},
    ]
    ranked = rank_candidates(candidates)
    assert ranked[0]["final_score"] == 82.0
    assert ranked[1]["final_score"] == 63.0
    assert ranked[2]["final_score"] == 45.0
    assert ranked[0]["rank"] == 1
    assert ranked[2]["rank"] == 3


def test_detect_fraud_short_resume():
    """Test that very short resumes are flagged."""
    from scoring.scorer import detect_fraud
    short_text = "Python developer. Skills: Python."
    result = detect_fraud(short_text)
    assert result["is_suspicious"] is True
    assert result["risk_level"] in ["MEDIUM", "HIGH"]


def test_detect_fraud_normal_resume():
    """Test that a normal resume is not flagged."""
    from scoring.scorer import detect_fraud
    normal_text = """
    John Smith is a Senior Python Developer with 5 years of experience.
    He has worked at TechCorp building scalable APIs using FastAPI and PostgreSQL.
    His skills include Python, Docker, Kubernetes, and machine learning.
    He holds a Bachelor's degree in Computer Science from State University.
    He is proficient in Agile methodologies and has led teams of 4+ engineers.
    John is passionate about AI and NLP and has built production ML systems.
    He is available for full-time positions and can start immediately.
    References available upon request. Portfolio at github.com/johnsmith.
    """
    result = detect_fraud(normal_text)
    assert result["risk_level"] in ["LOW", "MEDIUM"]


def test_generate_feedback_missing_skills():
    """Test that feedback mentions missing skills."""
    from scoring.scorer import generate_feedback
    jd_features = {"skills": ["python", "docker", "kubernetes"], "experience_years": 3.0}
    resume_features = {"skills": ["python"], "experience_years": 1.0}
    score_result = {
        "final_score": 35.0,
        "missing_skills": ["docker", "kubernetes"],
        "experience_years": 1.0,
        "education": "bachelor",
    }
    feedback = generate_feedback(jd_features, resume_features, score_result)
    assert len(feedback) > 0
    assert any("docker" in f.lower() or "kubernetes" in f.lower() for f in feedback)


def test_scoring_weights_sum():
    """Test that scoring weights in config sum to 1.0."""
    from config import SKILL_WEIGHT, EXPERIENCE_WEIGHT, EDUCATION_WEIGHT
    total = SKILL_WEIGHT + EXPERIENCE_WEIGHT + EDUCATION_WEIGHT
    assert abs(total - 1.0) < 0.001, f"Weights sum to {total}, expected 1.0"
