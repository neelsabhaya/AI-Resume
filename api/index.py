"""
Vercel serverless function handler for FastAPI application.

This module wraps the FastAPI app using Mangum adapter to convert
ASGI application to AWS Lambda format (which Vercel uses).
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import main module
sys.path.insert(0, str(Path(__file__).parent.parent))

from mangum import Mangum
from main import app

# Create the handler that Vercel will use
handler = Mangum(app, lifespan="off")

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
