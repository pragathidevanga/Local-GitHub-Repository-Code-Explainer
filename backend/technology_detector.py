"""Dynamic technology and programming language detection based strictly on repo evidence."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Set

TECH_PATTERNS = {
    # Python frameworks & libraries
    "FastAPI": [r"fastapi", r"from fastapi import", r"import fastapi"],
    "Streamlit": [r"streamlit", r"import streamlit", r"st\."],
    "Django": [r"django", r"from django", r"import django"],
    "Flask": [r"flask", r"from flask import", r"import flask"],
    "PyTorch": [r"torch", r"import torch", r"from torch"],
    "TensorFlow": [r"tensorflow", r"import tensorflow", r"keras"],
    "Pandas": [r"pandas", r"import pandas"],
    "NumPy": [r"numpy", r"import numpy"],
    "Scikit-Learn": [r"sklearn", r"scikit-learn"],
    "Pydantic": [r"pydantic", r"from pydantic import"],
    "GitPython": [r"gitpython", r"import git"],
    "Requests": [r"requests", r"import requests"],
    "Uvicorn": [r"uvicorn"],
    "Celery": [r"celery"],
    "SQLAlchemy": [r"sqlalchemy"],
    "Aiohttp": [r"aiohttp"],

    # JavaScript / TypeScript / Node
    "React": [r"react", r"react-dom", r"from ['\"]react['\"]"],
    "Next.js": [r"next", r"next/head", r"next/router"],
    "Vue.js": [r"vue", r"from ['\"]vue['\"]"],
    "Angular": [r"@angular/core"],
    "Express.js": [r"express", r"require\(['\"]express['\"]\)"],
    "Node.js": [r"package\.json", r"process\.env", r"require\("],
    "TypeScript": [r"\.tsx?$", r"tsconfig\.json"],
    "Tailwind CSS": [r"tailwindcss", r"tailwind\.config"],
    "Vite": [r"vite", r"vite\.config"],
    "Webpack": [r"webpack"],

    # Java / Kotlin
    "Spring Boot": [r"org\.springframework\.boot", r"spring-boot"],
    "Maven": [r"pom\.xml"],
    "Gradle": [r"build\.gradle"],

    # Rust / Go / C++ / C#
    "Rust": [r"Cargo\.toml", r"\.rs$"],
    "Go": [r"go\.mod", r"\.go$"],
    ".NET / C#": [r"\.csproj$", r"\.sln$", r"using System;"],

    # Databases & Storage
    "PostgreSQL": [r"psycopg2", r"asyncpg", r"postgresql", r"postgres"],
    "MySQL": [r"mysql", r"pymysql"],
    "SQLite": [r"sqlite3", r"\.sqlite"],
    "MongoDB": [r"pymongo", r"mongoose", r"mongodb"],
    "Redis": [r"redis", r"ioredis"],

    # DevOps & Infrastructure
    "Docker": [r"dockerfile", r"docker-compose"],
    "GitHub Actions": [r"\.github/workflows"],
    "Kubernetes": [r"k8s", r"kubectl", r"helm"],
}

LANGUAGE_BY_EXT = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript (React)",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".java": "Java",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C/C++ Header",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby",
    ".kt": "Kotlin",
    ".swift": "Swift",
    ".dart": "Dart",
    ".r": "R",
    ".sql": "SQL",
    ".sh": "Shell Script",
    ".bat": "Batch Script",
    ".ps1": "PowerShell",
    ".html": "HTML",
    ".css": "CSS",
    ".ipynb": "Jupyter Notebook",
}


def detect_technologies(
    file_map: Dict[str, Path],
    manifest_contents: Dict[str, str],
    language_counts: Dict[str, int],
) -> List[str]:
    """Detect technologies and frameworks strictly supported by repository file evidence."""
    detected: Set[str] = set()

    # 1. Primary languages from file extension counts
    for lang, count in language_counts.items():
        if count > 0:
            detected.add(lang)

    # 2. Check manifests (package.json, requirements.txt, pyproject.toml, etc.)
    combined_manifests = "\n".join(manifest_contents.values()).lower()

    for tech_name, patterns in TECH_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, combined_manifests, re.IGNORECASE):
                detected.add(tech_name)
                break

    # 3. Check filenames & directory structures
    all_rel_paths = list(file_map.keys())
    for rel_path in all_rel_paths:
        lower_path = rel_path.lower()
        if "dockerfile" in lower_path or "docker-compose" in lower_path:
            detected.add("Docker")
        if ".github/workflows" in lower_path:
            detected.add("GitHub Actions")
        if lower_path.endswith(".ipynb"):
            detected.add("Jupyter Notebook")

    return sorted(list(detected))
