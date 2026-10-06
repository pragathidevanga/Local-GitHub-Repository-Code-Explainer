"""File inspection, binary check, sensitive file shielding, and Jupyter notebook parser."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Tuple

# Sensitive file names and patterns to shield
SENSITIVE_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.staging",
    ".env.development",
    ".env.test",
    "credentials",
    "id_rsa",
    "id_rsa.pub",
    "id_ecdsa",
    "id_ed25519",
    "secrets.yml",
    "secrets.yaml",
    "secrets.json",
    "service_account.json",
}

SENSITIVE_PATTERNS = [
    r"\.pem$",
    r"\.key$",
    r"\.pkcs12$",
    r"\.pfx$",
    r"\.asc$",
    r"id_rsa",
    r"token",
    r"secret",
    r"credential",
    r"password",
]

BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".webp",
    ".pdf", ".zip", ".tar", ".gz", ".7z", ".rar", ".bz2",
    ".exe", ".dll", ".so", ".dylib", ".bin", ".dat", ".db", ".sqlite", ".sqlite3",
    ".pyc", ".pyo", ".pyd", ".class", ".o", ".obj",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".mp3", ".mp4", ".wav", ".avi", ".mov", ".flv",
}

DEPENDENCY_MANIFESTS = {
    "requirements.txt", "package.json", "package-lock.json", "yarn.lock",
    "pyproject.toml", "setup.py", "setup.cfg", "Pipfile", "Pipfile.lock",
    "pom.xml", "build.gradle", "build.gradle.kts", "Cargo.toml", "Cargo.lock",
    "go.mod", "go.sum", "composer.json", "composer.lock", "Gemfile", "Gemfile.lock",
}

DEPLOYMENT_FILES = {
    "dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "procfile", "fly.toml", "render.yaml", "netlify.toml", "vercel.json",
}

SOURCE_EXTENSIONS = {
    ".py", ".java", ".js", ".jsx", ".ts", ".tsx", ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp",
    ".cs", ".go", ".rs", ".php", ".rb", ".kt", ".kts", ".swift", ".dart", ".r",
    ".sql", ".sh", ".bash", ".zsh", ".bat", ".ps1", ".m", ".mm", ".scala", ".groovy",
    ".lua", ".perl", ".pl", ".asm", ".s", ".v", ".vhdl", ".f90", ".f", ".erl", ".ex", ".exs",
}

DOCUMENTATION_EXTENSIONS = {".md", ".rst", ".txt", ".adoc", ".markdown"}
CONFIGURATION_EXTENSIONS = {".yaml", ".yml", ".json", ".toml", ".ini", ".conf", ".config", ".xml", ".properties"}
WEB_EXTENSIONS = {".html", ".htm", ".css", ".scss", ".sass", ".less"}
DATA_EXTENSIONS = {".csv", ".tsv", ".jsonl", ".parquet", ".ndjson"}


def is_sensitive_file(rel_path: str) -> bool:
    """Check whether a relative file path matches sensitive security patterns."""
    file_name = Path(rel_path).name.lower()
    if file_name in SENSITIVE_FILENAMES:
        return True

    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, file_name, re.IGNORECASE):
            return True
    return False


def is_binary_file(file_path: Path) -> bool:
    """Check whether a file is binary using extension and initial byte inspection."""
    if file_path.suffix.lower() in BINARY_EXTENSIONS:
        return True

    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return True
    except Exception:
        return True

    return False


def classify_file(rel_path: str, file_path: Path) -> str:
    """Dynamically classify a file into one of 11 explicit categories."""
    path_obj = Path(rel_path)
    file_name = path_obj.name.lower()
    ext = path_obj.suffix.lower()
    parts_lower = [p.lower() for p in path_obj.parts]

    # Binary check
    if is_binary_file(file_path):
        return "binary"

    # Dependency check
    if file_name in DEPENDENCY_MANIFESTS:
        return "dependency"

    # Deployment / CI/CD check
    if file_name in DEPLOYMENT_FILES or ".github" in parts_lower or "docker" in file_name:
        return "deployment"

    # Notebook check
    if ext == ".ipynb":
        return "notebook"

    # Documentation check
    if file_name.startswith("readme") or ext in DOCUMENTATION_EXTENSIONS or "docs" in parts_lower or "doc" in parts_lower:
        return "documentation"

    # Test check
    if "test" in parts_lower or "tests" in parts_lower or file_name.startswith("test_") or file_name.endswith("_test.py") or file_name.endswith(".test.js") or file_name.endswith("test.java"):
        return "test"

    # Source code check
    if ext in SOURCE_EXTENSIONS:
        return "source"

    # Configuration check
    if ext in CONFIGURATION_EXTENSIONS:
        return "configuration"

    # Web check
    if ext in WEB_EXTENSIONS:
        return "web"

    # Data / Schema check
    if ext in DATA_EXTENSIONS or "schema" in file_name or file_name.endswith(".sql"):
        return "data_schema"

    return "unknown_text"


def read_text_file(file_path: Path, max_chars: int = 50000) -> Tuple[bool, str]:
    """Safely read text file content with encoding fallbacks and size limits."""
    if is_binary_file(file_path):
        return False, "[BINARY FILE - CONTENTS EXCLUDED]"

    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc, errors="replace") as f:
                content = f.read(max_chars)
                return True, content
        except Exception:
            continue

    return False, "[UNREADABLE TEXT FILE]"


def parse_jupyter_notebook(file_path: Path) -> str:
    """Parse Jupyter notebook (.ipynb) JSON, extracting Markdown & code cells cleanly."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)

        cells = data.get("cells", [])
        extracted_sections = []

        for idx, cell in enumerate(cells, start=1):
            cell_type = cell.get("cell_type", "unknown")
            source = "".join(cell.get("source", []))
            if not source.strip():
                continue

            if cell_type == "markdown":
                extracted_sections.append(f"--- [Notebook Markdown Cell {idx}] ---\n{source.strip()}")
            elif cell_type == "code":
                # We ignore execution outputs completely and only extract raw code
                extracted_sections.append(f"--- [Notebook Code Cell {idx}] ---\n{source.strip()}")

        if not extracted_sections:
            return "[Empty Jupyter Notebook]"

        return "\n\n".join(extracted_sections)
    except Exception as exc:
        return f"[Error parsing notebook JSON: {str(exc)}]"
