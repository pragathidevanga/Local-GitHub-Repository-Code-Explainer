from __future__ import annotations

import json
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .utils import is_sensitive, should_ignore

LANGUAGE_MAP = {
    ".py": "Python", ".pyw": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".java": "Java", ".c": "C", ".h": "C/C++",
    ".cpp": "C++", ".cc": "C++", ".cxx": "C++", ".cs": "C#", ".go": "Go", ".rs": "Rust",
    ".php": "PHP", ".rb": "Ruby", ".kt": "Kotlin", ".kts": "Kotlin", ".swift": "Swift",
    ".dart": "Dart", ".r": "R", ".R": "R", ".m": "MATLAB", ".sql": "SQL",
    ".html": "HTML", ".htm": "HTML", ".css": "CSS", ".scss": "SCSS", ".sass": "Sass",
    ".vue": "Vue", ".svelte": "Svelte", ".lua": "Lua", ".scala": "Scala", ".sh": "Shell",
    ".bash": "Shell", ".ps1": "PowerShell", ".pl": "Perl", ".ex": "Elixir", ".exs": "Elixir",
    ".fs": "F#", ".fsx": "F#", ".hs": "Haskell", ".groovy": "Groovy", ".jl": "Julia",
}

CATEGORY_BY_EXT = {
    ".ipynb": "notebook",
    ".md": "documentation", ".mdx": "documentation", ".rst": "documentation", ".txt": "documentation",
    ".adoc": "documentation", ".tex": "documentation",
    ".yaml": "configuration", ".yml": "configuration", ".json": "configuration", ".toml": "configuration",
    ".ini": "configuration", ".cfg": "configuration", ".conf": "configuration", ".xml": "configuration",
    ".properties": "configuration", ".env.example": "configuration",
    ".csv": "data/schema", ".tsv": "data/schema", ".parquet": "data/schema", ".sql": "source",
    ".html": "markup", ".htm": "markup", ".css": "style", ".scss": "style", ".sass": "style",
    ".test.js": "test", ".spec.js": "test", ".test.ts": "test", ".spec.ts": "test",
    ".test.py": "test", ".spec.py": "test",
    ".png": "asset", ".jpg": "asset", ".jpeg": "asset", ".gif": "asset", ".webp": "asset",
    ".svg": "asset", ".ico": "asset", ".mp3": "asset", ".wav": "asset", ".mp4": "asset",
    ".mov": "asset", ".avi": "asset", ".pdf": "asset", ".zip": "binary", ".7z": "binary",
    ".exe": "binary", ".dll": "binary", ".so": "binary", ".bin": "binary",
}

KNOWN_BUILD_FILES = {
    "dockerfile", "makefile", "procfile", "jenkinsfile", "justfile", "taskfile.yml", "compose.yml",
    "compose.yaml", "docker-compose.yml", "docker-compose.yaml", "package.json", "requirements.txt",
    "pyproject.toml", "poetry.lock", "pipfile", "pipfile.lock", "package-lock.json", "yarn.lock",
    "pnpm-lock.yaml", "cargo.toml", "go.mod", "pom.xml", "build.gradle", "composer.json", "gemfile",
}

SOURCE_TOKENS = (
    "import ", "from ", "def ", "class ", "function ", "const ", "let ", "var ", "public class",
    "package ", "func ", "fn ", "using ", "namespace ", "SELECT ", "CREATE TABLE", "<!doctype",
)


@dataclass
class InspectedFile:
    path: str
    category: str
    language: str | None
    size: int
    readable: bool
    sensitive: bool
    binary: bool
    content: str = ""
    truncated: bool = False


def _is_probably_binary(raw: bytes) -> bool:
    if not raw:
        return False
    if b"\x00" in raw[:4096]:
        return True
    sample = raw[:4096]
    printable = sum(1 for b in sample if b in (9, 10, 13) or 32 <= b <= 126)
    return printable / max(1, len(sample)) < 0.70


def _classify(path: Path, sample_text: str) -> tuple[str, str | None]:
    name = path.name.lower()
    suffix = path.suffix.lower()
    full_suffix = ''.join(path.suffixes[-2:]).lower()
    if name in KNOWN_BUILD_FILES:
        return "build/deployment", None
    path_parts = {part.lower() for part in path.parts}
    if {"test", "tests", "__tests__"}.intersection(path_parts):
        return "test", LANGUAGE_MAP.get(suffix)
    if name.startswith("readme") or name.startswith("changelog") or name.startswith("license"):
        return "documentation", None
    dependency_name = {
        "requirements.txt", "requirements-dev.txt", "requirements-prod.txt", "package.json",
        "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "pyproject.toml", "pom.xml",
        "build.gradle", "cargo.toml", "go.mod", "composer.json", "gemfile",
    }
    if name in dependency_name:
        return "configuration", None
    if full_suffix in CATEGORY_BY_EXT:
        category = CATEGORY_BY_EXT[full_suffix]
    elif suffix in CATEGORY_BY_EXT:
        category = CATEGORY_BY_EXT[suffix]
    else:
        category = "unknown text"
    if category == "source" and (name.endswith(".test.js") or name.endswith(".spec.js") or name.endswith(".test.py") or name.endswith(".spec.py")):
        category = "test"
    language = LANGUAGE_MAP.get(suffix)
    if category == "unknown text":
        lowered = sample_text.lower()
        if any(token.lower() in lowered[:5000] for token in SOURCE_TOKENS):
            category = "source"
    return category, language


def inspect_repository(root: Path, max_preview_bytes: int = 64_000) -> list[InspectedFile]:
    results: list[InspectedFile] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or should_ignore(path):
            continue
        rel = path.relative_to(root).as_posix()
        sensitive = is_sensitive(path)
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if sensitive:
            results.append(InspectedFile(rel, "sensitive", None, size, False, True, True))
            continue
        try:
            raw = path.read_bytes() if size <= max_preview_bytes * 4 else path.open("rb").read(max_preview_bytes)
        except OSError:
            continue
        binary = _is_probably_binary(raw)
        if binary:
            results.append(InspectedFile(rel, "binary", None, size, False, False, True))
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("utf-8", errors="replace")
        category, language = _classify(path, text)
        truncated = size > len(raw)
        if path.suffix.lower() == ".ipynb":
            text = _notebook_to_text(text, max_preview_bytes)
        results.append(InspectedFile(rel, category, language, size, True, False, False, text, truncated))
    return results


def _notebook_to_text(raw_json: str, max_chars: int) -> str:
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError:
        return raw_json[:max_chars]
    chunks: list[str] = []
    for idx, cell in enumerate(payload.get("cells", []), start=1):
        cell_type = cell.get("cell_type", "unknown")
        source = cell.get("source", [])
        source_text = "".join(source) if isinstance(source, list) else str(source)
        if not source_text.strip():
            continue
        chunks.append(f"[Cell {idx} | {cell_type}]\n{source_text.strip()}")
    return "\n\n".join(chunks)[:max_chars]


def summarize_counts(files: Iterable[InspectedFile]) -> dict[str, int]:
    counts = {
        "total_files": 0, "source_files": 0, "notebook_files": 0, "documentation_files": 0,
        "configuration_files": 0, "data_schema_files": 0, "test_files": 0, "asset_files": 0,
        "binary_files": 0, "unknown_text_files": 0,
    }
    for file in files:
        counts["total_files"] += 1
        mapping = {
            "source": "source_files", "notebook": "notebook_files", "documentation": "documentation_files",
            "configuration": "configuration_files", "data/schema": "data_schema_files", "test": "test_files",
            "asset": "asset_files", "binary": "binary_files", "unknown text": "unknown_text_files",
            "markup": "source_files", "style": "source_files", "build/deployment": "configuration_files",
        }
        key = mapping.get(file.category)
        if key:
            counts[key] += 1
    return counts
