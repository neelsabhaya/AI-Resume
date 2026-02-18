"""services/matcher.py

AI Matching Engine:
  - TF-IDF cosine similarity
  - Semantic similarity via sentence-transformers
  - Blended final similarity score
"""
import logging
import numpy as np
from typing import Dict, Any, List
from functools import lru_cache

from config import SEMANTIC_BLEND

logger = logging.getLogger(__name__)

# Lazy-loaded models
_tfidf_vectorizer = None
_sentence_model = None


def _get_sentence_model():
    global _sentence_model
    if _sentence_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            from config import SENTENCE_TRANSFORMER_MODEL
            logger.info(f"Loading sentence-transformers model: {SENTENCE_TRANSFORMER_MODEL}")
            _sentence_model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
            logger.info("Sentence-transformers model loaded.")
        except Exception as e:
            logger.error(f"Failed to load sentence-transformers: {e}")
            raise
    return _sentence_model


def compute_tfidf_similarity(text1: str, text2: str) -> float:
    """
    Compute cosine similarity between two texts using TF-IDF vectors.
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words="english",
        )
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(score)
    except Exception as e:
        logger.error(f"TF-IDF similarity error: {e}")
        return 0.0


def compute_semantic_similarity(text1: str, text2: str) -> float:
    """
    Compute cosine similarity between two texts using sentence embeddings.
    """
    try:
        from sklearn.metrics.pairwise import cosine_similarity
        model = _get_sentence_model()

        # Truncate to avoid token limits
        t1 = text1[:3000]
        t2 = text2[:3000]

        embeddings = model.encode([t1, t2], convert_to_numpy=True)
        score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return float(np.clip(score, 0.0, 1.0))
    except Exception as e:
        logger.error(f"Semantic similarity error: {e}")
        return 0.0


def compute_skill_overlap(jd_skills: List[str], resume_skills: List[str]) -> float:
    """
    Compute Jaccard-like skill overlap score between JD and resume skills.
    """
    if not jd_skills:
        return 0.5  # No JD skills specified → neutral score
    jd_set = set(jd_skills)
    resume_set = set(resume_skills)
    intersection = jd_set & resume_set
    # Score = matched / required (capped at 1.0)
    score = len(intersection) / len(jd_set)
    return float(min(score, 1.0))


def match_resume_to_jd(
    jd_features: Dict[str, Any],
    resume_features: Dict[str, Any],
) -> Dict[str, float]:
    """
    Compute all similarity scores between a JD and a resume.

    Returns:
        Dict with keys:
          - tfidf_score: float [0, 1]
          - semantic_score: float [0, 1]
          - skill_overlap: float [0, 1]
          - blended_text_score: float [0, 1]  (weighted blend of tfidf + semantic)
          - matched_skills: List[str]
          - missing_skills: List[str]
    """
    jd_text = jd_features.get("raw_text", "")
    resume_text = resume_features.get("raw_text", "")
    jd_skills = jd_features.get("skills", [])
    resume_skills = resume_features.get("skills", [])

    tfidf_score = compute_tfidf_similarity(jd_text, resume_text)
    semantic_score = compute_semantic_similarity(jd_text, resume_text)

    # Blend TF-IDF and semantic scores
    blended = (SEMANTIC_BLEND * semantic_score) + ((1 - SEMANTIC_BLEND) * tfidf_score)

    skill_overlap = compute_skill_overlap(jd_skills, resume_skills)

    matched_skills = sorted(set(jd_skills) & set(resume_skills))
    missing_skills = sorted(set(jd_skills) - set(resume_skills))

    return {
        "tfidf_score": round(tfidf_score, 4),
        "semantic_score": round(semantic_score, 4),
        "blended_text_score": round(blended, 4),
        "skill_overlap": round(skill_overlap, 4),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }
