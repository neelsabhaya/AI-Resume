"""scoring/scorer.py

Weighted scoring engine and candidate ranking.
Also handles fraud detection and AI feedback generation.
"""
import re
import logging
from typing import Dict, Any, List

from config import (
    SKILL_WEIGHT, EXPERIENCE_WEIGHT, EDUCATION_WEIGHT,
    EDUCATION_SCORES, FRAUD_KEYWORD_DENSITY_THRESHOLD, FRAUD_MIN_WORD_COUNT,
)

logger = logging.getLogger(__name__)

# Experience scoring: years → normalized score (0–1)
def _experience_score(years: float, required_years: float = 3.0) -> float:
    """Score experience relative to required years. Caps at 1.0."""
    if required_years <= 0:
        required_years = 3.0
    score = years / required_years
    return float(min(score, 1.0))


def _education_score(education_keyword: str) -> float:
    """Map education keyword to a normalized score (0–1)."""
    edu_lower = education_keyword.lower()
    for key, val in EDUCATION_SCORES.items():
        if key in edu_lower:
            return val
    return 0.30  # Default for unknown


def score_candidate(
    jd_features: Dict[str, Any],
    resume_features: Dict[str, Any],
    match_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compute a weighted final score (0–100) for a candidate.

    Scoring breakdown:
      - Skills (40%): skill overlap score from matcher
      - Experience (35%): years vs JD required years
      - Education (25%): education level score

    Returns:
        Dict with final_score, breakdown, fit_percentage, grade
    """
    # Skills component
    skill_score = match_result.get("skill_overlap", 0.0)

    # Experience component
    resume_exp = resume_features.get("experience_years", 0.0)
    jd_exp = jd_features.get("experience_years", 3.0)
    exp_score = _experience_score(resume_exp, jd_exp)

    # Education component
    edu_keyword = resume_features.get("education", "unknown")
    edu_score = _education_score(edu_keyword)

    # Text similarity bonus (blended semantic + TF-IDF) — used as a modifier
    text_similarity = match_result.get("blended_text_score", 0.0)

    # Weighted score (0–1)
    weighted = (
        SKILL_WEIGHT * skill_score +
        EXPERIENCE_WEIGHT * exp_score +
        EDUCATION_WEIGHT * edu_score
    )

    # Apply text similarity as a 20% modifier on top of weighted score
    final_raw = (0.80 * weighted) + (0.20 * text_similarity)
    final_score = round(final_raw * 100, 2)  # Convert to 0–100

    # Grade
    if final_score >= 80:
        grade = "A"
    elif final_score >= 65:
        grade = "B"
    elif final_score >= 50:
        grade = "C"
    elif final_score >= 35:
        grade = "D"
    else:
        grade = "F"

    return {
        "final_score": final_score,
        "fit_percentage": final_score,
        "grade": grade,
        "breakdown": {
            "skills_score": round(skill_score * 100, 2),
            "experience_score": round(exp_score * 100, 2),
            "education_score": round(edu_score * 100, 2),
            "text_similarity_score": round(text_similarity * 100, 2),
        },
        "matched_skills": match_result.get("matched_skills", []),
        "missing_skills": match_result.get("missing_skills", []),
        "experience_years": resume_exp,
        "education": edu_keyword,
    }


def rank_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort candidates by final_score descending and assign ranks.
    Each candidate dict must have a 'final_score' key.
    """
    sorted_candidates = sorted(
        candidates, key=lambda c: c.get("final_score", 0), reverse=True
    )
    for i, candidate in enumerate(sorted_candidates):
        candidate["rank"] = i + 1
    return sorted_candidates


def detect_fraud(resume_text: str) -> Dict[str, Any]:
    """
    Detect potentially fraudulent or low-quality resumes.

    Checks:
      1. Too short (< FRAUD_MIN_WORD_COUNT words)
      2. Keyword stuffing (single word > threshold% of all words)
      3. No coherent sentences (very few periods/newlines)

    Returns:
        Dict with is_suspicious (bool), reasons (List[str]), risk_level (str)
    """
    reasons = []
    words = resume_text.lower().split()
    word_count = len(words)

    # Check 1: Too short
    if word_count < FRAUD_MIN_WORD_COUNT:
        reasons.append(f"Resume is very short ({word_count} words). Minimum expected: {FRAUD_MIN_WORD_COUNT}.")

    # Check 2: Keyword stuffing
    if word_count > 0:
        from collections import Counter
        word_freq = Counter(words)
        most_common_word, most_common_count = word_freq.most_common(1)[0]
        density = most_common_count / word_count
        if density > FRAUD_KEYWORD_DENSITY_THRESHOLD:
            reasons.append(
                f"Keyword stuffing detected: '{most_common_word}' appears {most_common_count} times "
                f"({density:.1%} of all words)."
            )

    # Check 3: No coherent structure
    sentence_endings = len(re.findall(r"[.!?]\s", resume_text))
    if word_count > 50 and sentence_endings < 3:
        reasons.append("Resume lacks coherent sentence structure (very few sentence endings detected).")

    is_suspicious = len(reasons) > 0
    if len(reasons) >= 2:
        risk_level = "HIGH"
    elif len(reasons) == 1:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "is_suspicious": is_suspicious,
        "risk_level": risk_level,
        "reasons": reasons,
    }


def generate_feedback(
    jd_features: Dict[str, Any],
    resume_features: Dict[str, Any],
    score_result: Dict[str, Any],
) -> List[str]:
    """
    Generate actionable AI feedback suggestions for a candidate.

    Returns:
        List of improvement suggestion strings.
    """
    suggestions = []
    missing_skills = score_result.get("missing_skills", [])
    exp_years = score_result.get("experience_years", 0.0)
    jd_exp = jd_features.get("experience_years", 3.0)
    edu = score_result.get("education", "unknown")
    final_score = score_result.get("final_score", 0)

    # Skills gap
    if missing_skills:
        top_missing = missing_skills[:5]
        suggestions.append(
            f"🎯 **Skills Gap**: Consider adding or highlighting these skills from the JD: "
            f"{', '.join(top_missing)}."
        )

    # Experience gap
    if jd_exp > 0 and exp_years < jd_exp:
        gap = jd_exp - exp_years
        suggestions.append(
            f"📅 **Experience Gap**: The role requires ~{jd_exp:.0f} years of experience. "
            f"Your resume shows ~{exp_years:.0f} years. "
            f"Highlight relevant projects or freelance work to bridge the {gap:.0f}-year gap."
        )

    # Education
    if edu == "unknown":
        suggestions.append(
            "🎓 **Education**: No education details detected. Add your degree, institution, and graduation year."
        )

    # Low score general advice
    if final_score < 50:
        suggestions.append(
            "📝 **Resume Content**: Your resume has low overall match. "
            "Tailor your resume specifically to this job description by mirroring key terms and phrases."
        )
        suggestions.append(
            "🔍 **ATS Optimization**: Use standard section headings (Experience, Education, Skills) "
            "and avoid tables or graphics that ATS systems cannot parse."
        )

    if not suggestions:
        suggestions.append(
            "✅ **Great Match!** Your resume aligns well with this job description. "
            "Ensure your contact information and LinkedIn profile are up to date."
        )

    return suggestions
