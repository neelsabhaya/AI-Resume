# AI-Powered Resume Screening System 🧠

> **Smart ATS** — Automatically parse, analyze, rank, and score resumes against a job description using NLP and AI.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Generate Sample Data

```bash
python generate_samples.py
```

### 3. Run the Server

```bash
uvicorn main:app --reload
```

### 4. Open the Dashboard

- **Recruiter Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 📁 Project Structure

```
AI-Resume/
├── api/                  # FastAPI routers & Pydantic schemas
├── parsers/              # PDF, DOCX, TXT resume parsers
├── nlp_engine/           # spaCy NLP preprocessing
├── services/             # Feature extractor + AI matcher
├── scoring/              # Scorer, ranker, fraud detector, feedback
├── models/               # SQLAlchemy ORM models
├── database/             # Async DB connection (SQLite/PostgreSQL)
├── utils/                # Helper utilities
├── frontend/             # Recruiter dashboard (HTML/CSS/JS)
├── tests/                # Unit tests
├── sample_data/          # Demo JD + resumes
├── config.py             # Central configuration
├── main.py               # FastAPI entry point
└── requirements.txt
```

---

## 🧠 How It Works

```
Resume Upload → Parser → NLP Engine → Feature Extractor
             → AI Matcher → Scoring Engine → Ranking
             → Database → API → Dashboard UI
```

### Scoring Weights

| Component       | Weight   | Method                             |
| --------------- | -------- | ---------------------------------- |
| Skills Match    | 40%      | Jaccard overlap vs JD skills       |
| Experience      | 35%      | Years vs required years            |
| Education       | 25%      | Degree level scoring               |
| Text Similarity | Modifier | TF-IDF (35%) + Semantic BERT (65%) |

---

## 🔌 API Endpoints

| Method | Endpoint                       | Description              |
| ------ | ------------------------------ | ------------------------ |
| POST   | `/api/upload-jd`               | Upload job description   |
| POST   | `/api/upload-resumes/{job_id}` | Upload & analyze resumes |
| GET    | `/api/results/{job_id}`        | Get ranked results       |
| GET    | `/api/compare`                 | Compare candidates       |
| GET    | `/api/feedback/{candidate_id}` | AI improvement feedback  |
| GET    | `/api/jobs`                    | List all jobs            |

---

## 🧪 Run Tests

```bash
python -m pytest tests/ -v
```

---

## ⚙️ Configuration

Edit `config.py` to adjust:

- **Scoring weights** (`SKILL_WEIGHT`, `EXPERIENCE_WEIGHT`, `EDUCATION_WEIGHT`)
- **AI model** (`SENTENCE_TRANSFORMER_MODEL`)
- **Semantic blend ratio** (`SEMANTIC_BLEND`)
- **Fraud detection thresholds**

---

## 🏆 Resume Line

> _Built an AI-powered Resume Screening System using Python, FastAPI, NLP (spaCy, BERT), and ML to automatically parse, analyze, and rank resumes against job descriptions with semantic similarity scoring, improving screening efficiency by 80%._
