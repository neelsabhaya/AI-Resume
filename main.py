"""main.py

FastAPI application entry point for the AI Resume Screening System.
Run with: uvicorn main:app --reload
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import APP_TITLE, APP_VERSION, APP_DESCRIPTION, DEBUG
from database.connection import engine, Base
from api.routes import router

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create all DB tables on startup."""
    logger.info("🚀 Starting AI Resume Screening System...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables created/verified.")
    logger.info(f"🌐 Dashboard: http://localhost:8000")
    logger.info(f"📖 API Docs:  http://localhost:8000/docs")
    yield
    logger.info("👋 Shutting down...")


# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routes ─────────────────────────────────────────────────────────────────
app.include_router(router)

# ── Static Files (Frontend Dashboard) ─────────────────────────────────────────
frontend_dir = Path(__file__).parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_dashboard():
        """Serve the recruiter dashboard."""
        return FileResponse(str(frontend_dir / "index.html"))
else:
    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "message": f"Welcome to {APP_TITLE} v{APP_VERSION}",
            "docs": "/docs",
            "api": "/api",
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
