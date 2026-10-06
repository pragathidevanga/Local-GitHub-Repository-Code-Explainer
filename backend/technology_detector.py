from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Iterable

from .file_inspector import InspectedFile

TECH_RULES = {
    "Python": ["Python", "requirements.txt", "pyproject.toml", "setup.py", "Pipfile"],
    "JavaScript": ["JavaScript", "package.json", "package-lock.json"],
    "TypeScript": ["TypeScript", "tsconfig.json"],
    "React": ["react", "react-dom"],
    "Next.js": ["next"],
    "Vue": ["vue"],
    "Angular": ["@angular/core"],
    "Node.js": ["express", "fastify", "node"],
    "Express": ["express"],
    "FastAPI": ["fastapi"],
    "Flask": ["flask"],
    "Django": ["django"],
    "Streamlit": ["streamlit"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Scikit-learn": ["scikit-learn", "sklearn"],
    "PyTorch": ["torch", "pytorch"],
    "TensorFlow": ["tensorflow"],
    "MongoDB": ["pymongo", "mongoose", "mongodb"],
    "PostgreSQL": ["postgres", "psycopg", "postgresql"],
    "MySQL": ["mysql", "mysqlclient", "pymysql"],
    "SQLite": ["sqlite3", "sqlite"],
    "Docker": ["dockerfile", "docker-compose"],
    "GitHub Actions": [".github/workflows", "github actions"],
}


def detect_technologies(files: Iterable[InspectedFile]) -> list[str]:
    evidence = []
    for file in files:
        if file.category == "binary" or file.sensitive:
            continue
        text = file.content[:8000].lower()
        path = file.path.lower()
        evidence.append(path)
        evidence.append(text)
    combined = "\n".join(evidence)
    scores = Counter()
    for tech, tokens in TECH_RULES.items():
        for token in tokens:
            if token.lower() in combined:
                scores[tech] += 1
    for file in files:
        if file.language:
            scores[file.language] += 1
    return [name for name, _ in scores.most_common(20)]


def folder_tree(files: Iterable[InspectedFile]) -> list[str]:
    nodes: set[str] = set()
    for file in files:
        parts = Path(file.path).parts
        current = ""
        for part in parts[:-1]:
            current = f"{current}/{part}" if current else part
            nodes.add(current + "/")
        nodes.add(file.path)
    return sorted(nodes)
