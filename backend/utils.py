"""Utility functions for timing, path safety, and string sanitization."""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Tuple


class Timer:
    """Context manager for accurate millisecond timing using time.perf_counter()."""

    def __init__(self) -> None:
        self.start_time: float = 0.0
        self.elapsed_ms: float = 0.0

    def __enter__(self) -> Timer:
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.elapsed_ms = (time.perf_counter() - self.start_time) * 1000.0


def parse_github_url(url: str) -> Tuple[bool, str, str, str]:
    """Validate and extract (owner, repo_name, normalized_url) from a GitHub URL.

    Accepts HTTPS GitHub URLs from any public user/organization.
    Examples:
        https://github.com/user/repo
        https://github.com/user/repo.git
        https://github.com/user/repo/
    """
    if not url or not isinstance(url, str):
        return False, "", "", "URL must be a non-empty string"

    cleaned_url = url.strip().rstrip("/")
    if cleaned_url.endswith(".git"):
        cleaned_url = cleaned_url[:-4]

    pattern = r"^https?://(?:www\.)?github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)$"
    match = re.match(pattern, cleaned_url)

    if not match:
        return (
            False,
            "",
            "",
            "Invalid GitHub URL format. Expected: https://github.com/owner/repository",
        )

    owner = match.group(1)
    repo = match.group(2)
    normalized_url = f"https://github.com/{owner}/{repo}.git"
    return True, owner, repo, normalized_url


def sanitize_text(text: str) -> str:
    """Sanitize raw text for safe display and prompt construction."""
    if not text:
        return ""
    # Remove null bytes or non-printable control characters (except newline, tab, carriage return)
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
    return cleaned
