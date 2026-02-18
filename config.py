"""
config.py — Central configuration for the AI Resume Screening System.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "uploads")
# Only create directories if not in serverless environment (Vercel)
# In serverless, use /tmp for temporary storage
IS_SERVERLESS = os.getenv("VERCEL", "false").lower() == "true"
if not IS_SERVERLESS:
    UPLOAD_DIR.mkdir(exist_ok=True)
else:
    # Use /tmp in serverless environment (only for temporary storage)
    UPLOAD_DIR = Path("/tmp/uploads")
    UPLOAD_DIR.mkdir(exist_ok=True)

SAMPLE_DATA_DIR = BASE_DIR / "sample_data"
if not IS_SERVERLESS:
    SAMPLE_DATA_DIR.mkdir(exist_ok=True)

# ── Database ───────────────────────────────────────────────────────────────────
# Default to SQLite for local development, but strongly recommend PostgreSQL for production
# Serverless environments (Vercel) MUST use external database like PostgreSQL
if IS_SERVERLESS:
    # In serverless, require DATABASE_URL to be set (no SQLite default)
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    if not DATABASE_URL:
        # Fallback warning - app will fail if database operations are attempted
        print("WARNING: DATABASE_URL not set in serverless environment. Database operations will fail.")
        DATABASE_URL = "sqlite+aiosqlite:///./resume_ai.db"
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./resume_ai.db")

# ── AI / NLP ───────────────────────────────────────────────────────────────────
SPACY_MODEL = "en_core_web_sm"
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"

# ── Scoring Weights (must sum to 1.0) ─────────────────────────────────────────
SKILL_WEIGHT = 0.40
EXPERIENCE_WEIGHT = 0.35
EDUCATION_WEIGHT = 0.25

# Semantic vs TF-IDF blend (0 = pure TF-IDF, 1 = pure semantic)
SEMANTIC_BLEND = 0.65

# ── Education Level Scores ─────────────────────────────────────────────────────
EDUCATION_SCORES = {
    "phd": 1.0,
    "doctorate": 1.0,
    "master": 0.85,
    "mba": 0.85,
    "m.s": 0.85,
    "m.tech": 0.85,
    "bachelor": 0.70,
    "b.tech": 0.70,
    "b.e": 0.70,
    "b.sc": 0.65,
    "associate": 0.50,
    "diploma": 0.40,
    "high school": 0.20,
}

# ── App Meta ───────────────────────────────────────────────────────────────────
APP_TITLE = "AI Resume Screening System"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI-powered ATS that parses, analyzes, and ranks resumes against a job description."
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# ── Fraud Detection Thresholds ─────────────────────────────────────────────────
FRAUD_KEYWORD_DENSITY_THRESHOLD = 0.15   # >15% same keyword = suspicious
FRAUD_MIN_WORD_COUNT = 80                # resumes < 80 words are flagged
