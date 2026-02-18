"""tests/test_nlp.py"""
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_clean_text():
    """Test that clean_text removes URLs, emails, and special characters."""
    from nlp_engine.preprocessor import clean_text
    text = "Visit http://example.com or email me at john@test.com! Call +1-555-0101."
    result = clean_text(text)
    assert "http" not in result
    assert "@" not in result
    assert "example.com" not in result


def test_extract_skills_finds_python():
    """Test that Python is detected in resume text."""
    from services.extractor import extract_skills
    text = "I have 5 years of experience in Python, FastAPI, and PostgreSQL."
    skills = extract_skills(text)
    assert "python" in skills
    assert "fastapi" in skills
    assert "postgresql" in skills


def test_extract_experience_years():
    """Test experience year extraction from various patterns."""
    from services.extractor import extract_experience_years
    assert extract_experience_years("5 years of experience in Python") == 5.0
    assert extract_experience_years("3+ years experience") == 3.0
    assert extract_experience_years("No experience mentioned") == 0.0


def test_extract_education():
    """Test education level detection."""
    from services.extractor import extract_education
    assert "bachelor" in extract_education("Bachelor of Technology in CS")
    assert "master" in extract_education("Master of Science in AI")
    assert "phd" in extract_education("PhD in Computer Science")
    assert extract_education("No education mentioned") == "unknown"


def test_extract_features_returns_dict():
    """Test that extract_features returns a complete dict."""
    from services.extractor import extract_features
    text = "Python developer with 3 years experience. Bachelor in CS. Skills: FastAPI, Docker."
    features = extract_features(text)
    assert "skills" in features
    assert "experience_years" in features
    assert "education" in features
    assert "raw_text" in features
    assert isinstance(features["skills"], list)
    assert features["experience_years"] == 3.0
