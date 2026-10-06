from __future__ import annotations

import hashlib
import re
from pathlib import Path

SENSITIVE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "credentials.json",
    "service-account.json",
    "id_rsa",
    "id_ed25519",
    "private.key",
}
SENSITIVE_PARTS = {"secrets", "secret", "credentials", "credential", "private_keys"}
IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "target",
}


def is_sensitive(path: Path) -> bool:
    lowered = {part.lower() for part in path.parts}
    if path.name.lower() in SENSITIVE_NAMES:
        return True
    if lowered.intersection(SENSITIVE_PARTS):
        return True
    if path.suffix.lower() in {".pem", ".p12", ".pfx", ".key", ".crt"}:
        return True
    return False


def should_ignore(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def safe_job_id() -> str:
    import uuid

    return uuid.uuid4().hex


def redact_secrets(text: str) -> str:
    patterns = [
        (r"(?im)^([A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASS|CREDENTIAL)[A-Z0-9_]*)\s*=\s*[^\n]+$", r"\1=[REDACTED]"),
        (r"(?i)(api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*[\"']?[^\"'\s,;]+", r"\1=[REDACTED]"),
    ]
    out = text
    for pattern, repl in patterns:
        out = re.sub(pattern, repl, out)
    return out


def stable_short_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:12]
