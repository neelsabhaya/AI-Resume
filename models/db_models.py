"""models/db_models.py

SQLAlchemy ORM models for the Resume Screening System.
"""
import json
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from database.connection import Base


class Job(Base):
    """Represents a job posting with its description and extracted features."""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="Untitled Position")
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, default=list)
    required_experience_years = Column(Float, default=0.0)
    required_education = Column(String(100), default="unknown")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    candidates = relationship("Candidate", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Job id={self.id} title='{self.title}'>"


class Candidate(Base):
    """Represents a candidate who applied for a job."""
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    name = Column(String(255), default="Unknown")
    raw_text = Column(Text, default="")
    skills = Column(JSON, default=list)
    experience_years = Column(Float, default=0.0)
    education = Column(String(100), default="unknown")
    is_suspicious = Column(Boolean, default=False)
    fraud_risk_level = Column(String(10), default="LOW")
    fraud_reasons = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="candidates")
    score = relationship("Score", back_populates="candidate", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Candidate id={self.id} filename='{self.filename}'>"


class Score(Base):
    """Stores the AI-computed score and ranking for a candidate."""
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, unique=True)
    final_score = Column(Float, default=0.0)
    fit_percentage = Column(Float, default=0.0)
    grade = Column(String(2), default="F")
    rank = Column(Integer, default=0)
    skills_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    education_score = Column(Float, default=0.0)
    text_similarity_score = Column(Float, default=0.0)
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    feedback = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate", back_populates="score")

    def __repr__(self):
        return f"<Score candidate_id={self.candidate_id} score={self.final_score}>"
