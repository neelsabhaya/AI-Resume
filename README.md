# AI-Powered Resume Screening System 🧠

> **Smart ATS** — Automatically parse, analyze, rank, and score resumes against a job description using NLP and AI.

---

## 🚀 Quick Start

### 0. Requirements

- Python **3.10–3.13** (3.11 is recommended)
- Git (if you are cloning from GitHub)

> Note: Some optional NLP features (spaCy, sentence-transformers) may
> require extra build tools on newer Python versions. The core app
> (parsing, scoring, dashboard) works without them.

### 1. Clone & create virtual environment

```bash
git clone https://github.com/your-username/AI-Resume.git
cd AI-Resume

# Windows (PowerShell)
python -m venv .venv
./.venv/Scripts/Activate.ps1

# Windows (cmd)
:: python -m venv .venv
:: .\.venv\Scripts\activate
```

### 2. Install Python dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt

# (Optional, only if you want spaCy-based NLP and it installs cleanly)
# python -m spacy download en_core_web_sm
```

### 3. (Optional) Install OCR engine for scanned PDFs

PDFs that are **images only** (scanned resumes) can be read via OCR.
For that to work you need the Tesseract engine installed at the
system level:

- Official Tesseract project site: https://tesseract-ocr.github.io/
- Official source and docs: https://github.com/tesseract-ocr/tesseract

If you skip this step, text-based PDFs and DOCX/TXT resumes will still
work, but scanned PDFs may return "no text extracted".

### 4. Generate sample data (optional)

```bash
python generate_samples.py
```

This will create a demo job description and a few example resumes in
`sample_data/` so you can try the system quickly.

### 5. Run the Server

```bash
python -m uvicorn main:app --reload
```

### 6. Open the Dashboard

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

## 🚢 Deployment

### Deploy to Vercel (Serverless)

This application is configured for easy deployment to Vercel:

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Deploy to production
vercel --prod
```

**Important:** You must configure a PostgreSQL database for production. See [`DEPLOYMENT.md`](DEPLOYMENT.md) for complete instructions including:
- Step-by-step deployment guide (CLI and Dashboard methods)
- Database setup (PostgreSQL required)
- Environment variables configuration
- Serverless limitations and workarounds
- Performance optimization tips
- Troubleshooting guide

### Alternative Deployment Options

- **Docker**: Use Docker for containerized deployment on any platform
- **Traditional VPS**: Deploy on AWS EC2, DigitalOcean, or similar
- **Platform-as-a-Service**: Railway, Render, Fly.io, Google Cloud Run

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for detailed guidance on all deployment options.
