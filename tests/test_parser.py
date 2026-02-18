"""tests/test_parser.py"""
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_parse_txt_file(tmp_path):
    """Test that TXT files are parsed correctly."""
    from parsers.resume_parser import parse_txt
    test_file = tmp_path / "test_resume.txt"
    test_file.write_text("John Doe\nPython Developer\n5 years experience", encoding="utf-8")
    result = parse_txt(str(test_file))
    assert "John Doe" in result
    assert "Python Developer" in result


def test_parse_resume_unsupported_extension(tmp_path):
    """Test that unsupported file types return empty string."""
    from parsers.resume_parser import parse_resume
    test_file = tmp_path / "test.xyz"
    test_file.write_text("some content")
    result = parse_resume(str(test_file))
    assert result == ""


def test_parse_resume_dispatches_txt(tmp_path):
    """Test that parse_resume correctly dispatches to TXT parser."""
    from parsers.resume_parser import parse_resume
    test_file = tmp_path / "resume.txt"
    test_file.write_text("Alice Smith\nSoftware Engineer\n3 years Python experience")
    result = parse_resume(str(test_file))
    assert len(result) > 0
    assert "Alice Smith" in result
