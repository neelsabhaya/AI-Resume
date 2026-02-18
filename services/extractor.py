"""services/extractor.py

Extracts structured features from raw resume/JD text:
  - Skills (matched against a curated tech skills list)
  - Years of experience
  - Education level
"""
import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# ── Curated Skills List (300+ tech skills) ────────────────────────────────────
TECH_SKILLS = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "go", "golang",
    "rust", "swift", "kotlin", "scala", "r", "matlab", "perl", "ruby", "php",
    "bash", "shell", "powershell", "dart", "elixir", "haskell", "lua", "groovy",

    # Web Frontend
    "html", "css", "react", "reactjs", "react.js", "angular", "angularjs", "vue",
    "vuejs", "vue.js", "next.js", "nextjs", "nuxt", "svelte", "jquery", "bootstrap",
    "tailwind", "tailwindcss", "sass", "scss", "webpack", "vite", "babel",

    # Web Backend
    "node.js", "nodejs", "express", "expressjs", "fastapi", "flask", "django",
    "spring", "spring boot", "springboot", "asp.net", "laravel", "rails",
    "ruby on rails", "graphql", "rest", "restful", "grpc", "websocket",

    # Databases
    "sql", "mysql", "postgresql", "postgres", "sqlite", "mongodb", "redis",
    "cassandra", "dynamodb", "elasticsearch", "neo4j", "oracle", "mssql",
    "mariadb", "firebase", "supabase", "prisma", "sequelize", "sqlalchemy",

    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
    "terraform", "ansible", "jenkins", "github actions", "ci/cd", "cicd",
    "nginx", "apache", "linux", "ubuntu", "debian", "centos",

    # AI / ML / Data Science
    "machine learning", "deep learning", "neural network", "nlp",
    "natural language processing", "computer vision", "tensorflow", "pytorch",
    "keras", "scikit-learn", "sklearn", "pandas", "numpy", "matplotlib",
    "seaborn", "plotly", "opencv", "hugging face", "transformers", "bert",
    "gpt", "llm", "langchain", "xgboost", "lightgbm", "catboost",
    "random forest", "svm", "regression", "classification", "clustering",
    "reinforcement learning", "generative ai", "stable diffusion",
    "sentence transformers", "spacy", "nltk", "word2vec", "fasttext",

    # Data Engineering
    "spark", "apache spark", "hadoop", "kafka", "airflow", "dbt", "etl",
    "data pipeline", "data warehouse", "snowflake", "bigquery", "redshift",
    "databricks", "flink", "hive",

    # Tools & Practices
    "git", "github", "gitlab", "bitbucket", "jira", "confluence", "agile",
    "scrum", "kanban", "tdd", "bdd", "unit testing", "pytest", "jest",
    "selenium", "postman", "swagger", "openapi", "microservices",
    "system design", "design patterns", "solid", "oop", "functional programming",

    # Mobile
    "android", "ios", "react native", "flutter", "xamarin", "swift", "kotlin",

    # Security
    "cybersecurity", "penetration testing", "oauth", "jwt", "ssl", "tls",
    "encryption", "cryptography", "soc", "siem",
}

# ── Education Keywords ─────────────────────────────────────────────────────────
EDUCATION_KEYWORDS = [
    "phd", "ph.d", "doctorate", "doctor of",
    "master", "m.s", "m.sc", "m.tech", "m.e", "mba", "m.b.a",
    "bachelor", "b.tech", "b.e", "b.sc", "b.s", "b.a", "b.com",
    "associate", "diploma", "high school", "secondary",
]

# ── Experience Patterns ────────────────────────────────────────────────────────
EXPERIENCE_PATTERNS = [
    r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp|work)",
    r"(?:experience|exp)\s*(?:of\s+)?(\d+)\+?\s*(?:years?|yrs?)",
    r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:in\s+)?(?:the\s+)?(?:industry|field|domain)",
    r"worked?\s+(?:for\s+)?(\d+)\+?\s*(?:years?|yrs?)",
]


def extract_skills(text: str) -> List[str]:
    """
    Match skills from text against the curated TECH_SKILLS set.
    Uses case-insensitive substring matching.
    """
    text_lower = text.lower()
    found_skills = []
    for skill in TECH_SKILLS:
        # Use word boundary matching for short skills to avoid false positives
        if len(skill) <= 3:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        else:
            if skill in text_lower:
                found_skills.append(skill)
    return sorted(set(found_skills))


def extract_experience_years(text: str) -> float:
    """
    Extract the maximum years of experience mentioned in the text.
    Returns 0.0 if no experience found.
    """
    text_lower = text.lower()
    max_years = 0.0

    for pattern in EXPERIENCE_PATTERNS:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            try:
                years = float(match)
                if 0 < years <= 50:  # Sanity check
                    max_years = max(max_years, years)
            except ValueError:
                continue

    return max_years


def extract_education(text: str) -> str:
    """
    Detect the highest education level mentioned in the text.
    Returns the matched keyword or 'unknown'.
    """
    text_lower = text.lower()
    for keyword in EDUCATION_KEYWORDS:
        if keyword in text_lower:
            return keyword
    return "unknown"


def extract_features(text: str) -> Dict[str, Any]:
    """
    Master feature extractor. Returns a structured dict with:
      - skills: List[str]
      - experience_years: float
      - education: str
      - raw_text: str (for similarity computation)
    """
    return {
        "skills": extract_skills(text),
        "experience_years": extract_experience_years(text),
        "education": extract_education(text),
        "raw_text": text,
    }
