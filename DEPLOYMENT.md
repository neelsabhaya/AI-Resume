# Deployment Guide for AI-Resume on Vercel

This guide explains how to deploy the AI Resume Screening System to Vercel's serverless platform.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Deployment Methods](#deployment-methods)
  - [Method 1: Vercel Dashboard (Recommended for first-time)](#method-1-vercel-dashboard)
  - [Method 2: Vercel CLI](#method-2-vercel-cli)
- [Environment Variables](#environment-variables)
- [Database Configuration](#database-configuration)
- [Serverless Limitations & Workarounds](#serverless-limitations--workarounds)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)
- [Alternative Deployment Options](#alternative-deployment-options)

---

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code must be in a Git repository
3. **PostgreSQL Database**: Required for production (see [Database Configuration](#database-configuration))
4. **Vercel CLI** (for CLI deployment): `npm install -g vercel`

---

## Quick Start

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login to Vercel
vercel login

# 3. Deploy (from project root)
vercel

# 4. Follow prompts to configure your project
# 5. Set environment variables (see below)
# 6. Deploy to production
vercel --prod
```

---

## Deployment Methods

### Method 1: Vercel Dashboard

**Step-by-step:**

1. **Import Project**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Click "Import Git Repository"
   - Select your `AI-Resume` repository
   - Click "Import"

2. **Configure Project**
   - **Framework Preset**: Select "Other"
   - **Build Settings**: Leave as default (Vercel will auto-detect `vercel.json`)
   - **Root Directory**: Leave as `./` (root)

3. **Set Environment Variables**
   - Click "Environment Variables"
   - Add the following (see [Environment Variables](#environment-variables) section):
     ```
     DATABASE_URL=postgresql://...
     DEBUG=false
     ```
   - Apply to: **Production**, **Preview**, and **Development**

4. **Deploy**
   - Click "Deploy"
   - Wait 3-5 minutes for build and deployment
   - Visit the provided URL (e.g., `https://your-app.vercel.app`)

5. **Verify Deployment**
   - Visit `/` to see the dashboard
   - Visit `/api/jobs` to test the API
   - Visit `/docs` for API documentation

---

### Method 2: Vercel CLI

**Step-by-step:**

```bash
# 1. Login to Vercel
vercel login

# 2. Initialize project (first time only)
vercel
# - Set up and deploy: Yes
# - Which scope: [Select your account]
# - Link to existing project: No
# - What's your project's name: ai-resume
# - In which directory is your code located: ./

# 3. Set environment variables
vercel env add DATABASE_URL
# Paste your PostgreSQL connection string when prompted
# Select environments: Production, Preview, Development

vercel env add DEBUG
# Enter: false
# Select environments: Production, Preview, Development

# 4. Deploy to production
vercel --prod

# 5. View deployment
vercel open
```

**Useful CLI Commands:**
```bash
vercel              # Deploy to preview
vercel --prod       # Deploy to production
vercel env ls       # List environment variables
vercel logs         # View deployment logs
vercel inspect      # Inspect deployment details
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `DATABASE_URL` | **REQUIRED** PostgreSQL connection string | `postgresql://user:pass@host:5432/db` | None (required) |
| `DEBUG` | Enable debug mode (set to `false` in production) | `false` | `true` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_TITLE` | Application title | `AI Resume Screening System` |
| `UPLOAD_DIR` | Upload directory (use `/tmp` in serverless) | `./uploads` |
| `SPACY_MODEL` | spaCy model name | `en_core_web_sm` |
| `SENTENCE_TRANSFORMER_MODEL` | Sentence transformer model | `all-MiniLM-L6-v2` |
| `SKILL_WEIGHT` | Skills scoring weight | `0.4` |
| `EXPERIENCE_WEIGHT` | Experience scoring weight | `0.35` |
| `EDUCATION_WEIGHT` | Education scoring weight | `0.25` |

### Setting Environment Variables

**Via Dashboard:**
1. Go to your project on Vercel
2. Click "Settings" → "Environment Variables"
3. Add variables and select environments

**Via CLI:**
```bash
vercel env add VARIABLE_NAME
# Enter value when prompted
# Select environments
```

---

## Database Configuration

### Why PostgreSQL is Required

**SQLite Limitations in Serverless:**
- ❌ No persistent filesystem (files reset between invocations)
- ❌ Not suitable for concurrent access
- ❌ Database file lost after function execution

**PostgreSQL Benefits:**
- ✅ Persistent external storage
- ✅ Handles concurrent connections
- ✅ Production-ready scalability
- ✅ Connection pooling support

### Database Options

#### Option 1: Vercel Postgres (Recommended)

**Pros:** Integrated with Vercel, easy setup, low latency

```bash
# Install Vercel Postgres
vercel integration add postgres

# This automatically sets DATABASE_URL in your project
```

**Pricing:**
- Free tier: 256 MB storage, 60 compute hours/month
- Pro: $10/month base + usage

#### Option 2: External Providers

**Popular Options:**
- [Supabase](https://supabase.com) - Free tier: 500 MB, 2 CPU
- [Neon](https://neon.tech) - Free tier: 3 GB, serverless Postgres
- [Railway](https://railway.app) - Free tier: $5 credit/month
- [AWS RDS](https://aws.amazon.com/rds/) - Full control, higher cost
- [Heroku Postgres](https://www.heroku.com/postgres) - Free tier available

**Connection String Format:**
```
postgresql://username:password@host:port/database?sslmode=require
```

### Database Setup

1. **Create Database** (using provider's dashboard)

2. **Get Connection String**
   - Copy the connection URL from your provider
   - Ensure it includes `?sslmode=require` for security

3. **Set Environment Variable**
   ```bash
   vercel env add DATABASE_URL
   # Paste: postgresql://user:pass@host:5432/dbname?sslmode=require
   ```

4. **Initialize Tables**
   - Tables are auto-created on first API call (see `main.py` lifespan)
   - Or run manually:
     ```python
     # In Python environment with DATABASE_URL set
     from database.connection import engine, Base
     from models.db_models import Job, Candidate, Score
     import asyncio
     
     async def init_db():
         async with engine.begin() as conn:
             await conn.run_sync(Base.metadata.create_all)
     
     asyncio.run(init_db())
     ```

---

## Serverless Limitations & Workarounds

### 1. **File Upload Persistence**

**Problem:**
- Uploaded files stored in `/tmp` are lost after function execution
- Each API call may hit a different serverless instance

**Solutions:**
- ✅ **Use Cloud Storage**: Store files in S3, Cloudflare R2, or Vercel Blob
- ✅ **Process Immediately**: Parse and extract data from uploads, then discard files
- ✅ **Store in Database**: Save extracted text/features to PostgreSQL

**Recommended Approach:**
```python
# In your upload handler
async def upload_resume(file: UploadFile):
    # 1. Parse file immediately
    text = await parse_resume(file)
    
    # 2. Extract features
    features = await extract_features(text)
    
    # 3. Save to database (persistent)
    await db.save_candidate(features)
    
    # 4. Don't rely on file persistence
```

### 2. **Cold Start Times**

**Problem:**
- First request after inactivity can take 10-30 seconds
- ML models (spaCy, sentence-transformers) are large and slow to load

**Solutions:**
- ✅ **Warm-up Requests**: Use external monitoring (e.g., UptimeRobot) to ping API every 5 minutes
- ✅ **Lazy Loading**: Load models only when needed
- ✅ **Model Caching**: Cache loaded models in memory (persist across warm starts)
- ⚠️ **Upgrade Plan**: Pro plan has lower cold start times

**Example Lazy Loading:**
```python
# In nlp_engine/preprocessor.py or services/extractor.py
_nlp_model = None

def get_nlp_model():
    global _nlp_model
    if _nlp_model is None:
        _nlp_model = spacy.load("en_core_web_sm")
    return _nlp_model
```

### 3. **Function Timeout**

**Limits:**
- Hobby Plan: **10 seconds**
- Pro Plan: **60 seconds**
- Enterprise: **900 seconds**

**Problem:**
- Processing multiple large resumes may exceed timeout
- ML inference can be slow

**Solutions:**
- ✅ **Batch Optimization**: Process resumes in smaller batches
- ✅ **Async Processing**: Return immediately, process in background (requires external queue)
- ✅ **Upgrade Plan**: Pro plan gives 60s timeout
- ✅ **Offload Heavy Tasks**: Use background jobs (e.g., Vercel Cron, external worker)

### 4. **Package Size Limits**

**Limits:**
- Total deployment size: **250 MB** (includes dependencies)
- Model files (spaCy, sentence-transformers) are large

**Solutions:**
- ✅ **Smaller Models**: Use `en_core_web_sm` (14 MB) instead of `en_core_web_lg` (741 MB)
- ✅ **Lazy Downloads**: Download models on first run (store in `/tmp` or external cache)
- ✅ **Optimize Dependencies**: Remove unused packages

**Check Deployment Size:**
```bash
# See deployment bundle size
vercel inspect [deployment-url] --logs
```

### 5. **No Persistent Filesystem**

**Problem:**
- SQLite database resets between invocations
- Uploaded files disappear

**Solution:**
- ✅ **Use PostgreSQL** (external, persistent)
- ✅ **Use Object Storage** for files (S3, Vercel Blob)

---

## Performance Optimization

### 1. **Optimize Model Loading**

```python
# Cache models globally
import functools

@functools.lru_cache(maxsize=1)
def load_sentence_transformer():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")

@functools.lru_cache(maxsize=1)
def load_spacy_model():
    import spacy
    return spacy.load("en_core_web_sm")
```

### 2. **Database Connection Pooling**

Already configured in `database/connection.py` with async SQLAlchemy.

For high traffic, consider:
```python
# In database/connection.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,          # Max connections in pool
    max_overflow=10,      # Additional connections if pool exhausted
    pool_pre_ping=True,   # Verify connection before using
    pool_recycle=3600,    # Recycle connections every hour
)
```

### 3. **Enable Response Caching**

```python
# Add caching headers for static API responses
from fastapi import Response

@app.get("/api/jobs")
async def get_jobs(response: Response):
    response.headers["Cache-Control"] = "public, max-age=60"
    # ... your code
```

---

## Troubleshooting

### Issue: "Database connection failed"

**Cause:** `DATABASE_URL` not set or incorrect

**Solution:**
```bash
# Verify environment variable
vercel env ls

# Add/update DATABASE_URL
vercel env add DATABASE_URL
```

### Issue: "Function timeout exceeded"

**Cause:** Processing takes >10s (Hobby) or >60s (Pro)

**Solutions:**
1. Reduce number of resumes processed per request
2. Optimize ML model loading (lazy load, cache)
3. Upgrade to Pro plan for 60s timeout
4. Split into multiple API calls

### Issue: "Module not found" or "Import error"

**Cause:** Dependency missing or incorrect Python version

**Solutions:**
```bash
# Ensure all dependencies are in requirements.txt
pip freeze > requirements.txt

# Verify Python version in vercel.json (3.10 or 3.11)
# Check build logs: vercel logs
```

### Issue: "Cold start takes 30+ seconds"

**Cause:** Large ML models loading on first request

**Solutions:**
1. Use warm-up service (ping API every 5 min)
2. Implement lazy loading
3. Consider smaller models
4. Upgrade to Pro plan

### Issue: "File not found after upload"

**Cause:** Serverless filesystem is ephemeral

**Solution:**
- Process files immediately and store results in database
- Use external storage (S3, Vercel Blob) for persistence

---

## Alternative Deployment Options

If Vercel's serverless limitations are too restrictive:

### 1. **Docker + Container Platforms**
- **Platforms**: Railway, Render, Fly.io, DigitalOcean App Platform
- **Pros**: Persistent filesystem, longer timeouts, more control
- **Cons**: More expensive, requires Docker knowledge

### 2. **Traditional VPS**
- **Platforms**: AWS EC2, DigitalOcean Droplets, Linode
- **Pros**: Full control, no timeouts, persistent storage
- **Cons**: Manual setup, maintenance overhead, higher cost

### 3. **Managed Python Hosting**
- **Platforms**: PythonAnywhere, Google Cloud Run, AWS App Runner
- **Pros**: Python-optimized, easier than VPS
- **Cons**: More expensive than Vercel

### 4. **Kubernetes**
- **Platforms**: GKE, EKS, AKS, DigitalOcean Kubernetes
- **Pros**: Maximum scalability and control
- **Cons**: Complex setup, expensive, overkill for small apps

**Recommendation:**
- **For MVP/Testing**: Vercel (free tier)
- **For Production (light traffic)**: Vercel Pro ($20/month) or Railway ($5-20/month)
- **For Production (heavy traffic)**: Cloud Run, AWS App Runner, or Kubernetes

---

## Production Checklist

Before going live:

- [ ] Set `DEBUG=false` in environment variables
- [ ] Configure PostgreSQL database (not SQLite)
- [ ] Set up database backups
- [ ] Test all API endpoints
- [ ] Verify frontend loads correctly
- [ ] Set up error monitoring (Sentry, LogRocket)
- [ ] Configure custom domain (optional)
- [ ] Enable HTTPS (automatic on Vercel)
- [ ] Set up warm-up service to reduce cold starts
- [ ] Review Vercel usage limits and upgrade if needed
- [ ] Document API credentials and access

---

## Support & Resources

- **Vercel Docs**: https://vercel.com/docs
- **Vercel Python Runtime**: https://vercel.com/docs/functions/runtimes/python
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Mangum (ASGI Adapter)**: https://mangum.io/
- **Vercel Community**: https://github.com/vercel/vercel/discussions

---

## Summary

**Vercel Deployment is Suitable If:**
- ✅ You use PostgreSQL (not SQLite)
- ✅ Resume processing takes <10s (Hobby) or <60s (Pro)
- ✅ You process files immediately (don't store long-term)
- ✅ Traffic is moderate (cold starts acceptable)

**Consider Alternatives If:**
- ❌ You need persistent filesystem
- ❌ Processing takes >60 seconds
- ❌ You have high, sustained traffic (cold starts unacceptable)
- ❌ ML models are too large (>200 MB total)

For most use cases, Vercel is an excellent choice for fast, free/low-cost deployment with minimal configuration!
