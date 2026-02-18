"""utils/helpers.py

Utility functions for file validation and display formatting.
"""
from pathlib import Path
from typing import Tuple


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
MAX_FILE_SIZE_MB = 10


def validate_file(filename: str, file_size_bytes: int) -> Tuple[bool, str]:
    """
    Validate uploaded file by extension and size.

    Returns:
        (is_valid: bool, error_message: str)
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"

    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_bytes:
        return False, f"File too large ({file_size_bytes / 1024 / 1024:.1f} MB). Max: {MAX_FILE_SIZE_MB} MB"

    return True, ""


def format_score_display(score: float) -> str:
    """Format a 0–100 score as a display string with color hint."""
    if score >= 80:
        return f"🟢 {score:.1f}%"
    elif score >= 60:
        return f"🟡 {score:.1f}%"
    elif score >= 40:
        return f"🟠 {score:.1f}%"
    else:
        return f"🔴 {score:.1f}%"


def truncate_text(text: str, max_chars: int = 500) -> str:
    """Truncate text to max_chars with ellipsis."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."
