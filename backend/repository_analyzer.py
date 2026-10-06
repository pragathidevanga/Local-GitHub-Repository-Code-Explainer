from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from .file_inspector import InspectedFile, inspect_repository, summarize_counts
from .technology_detector import detect_technologies, folder_tree


def language_counts(files: list[InspectedFile]) -> dict[str, int]:
    counts = Counter(file.language for file in files if file.language and file.category not in {"binary", "sensitive"})
    return dict(counts.most_common())


def compact_summary(file: InspectedFile) -> str:
    if not file.readable:
        return "Non-text file; metadata only."
    text = file.content.strip()
    if not text:
        return "Readable but empty."
    first_lines = [line.strip() for line in text.splitlines() if line.strip()][:3]
    return " ".join(first_lines)[:280]


def analyze_repository(root: Path) -> dict:
    files = inspect_repository(root)
    counts = summarize_counts(files)
    meaningful = [f for f in files if f.category != "sensitive"]
    return {
        "files": files,
        "counts": counts,
        "languages": language_counts(files),
        "technologies": detect_technologies(files),
        "folder_tree": folder_tree(files),
        "file_summaries": [
            {
                "path": f.path,
                "category": f.category,
                "language": f.language,
                "size": f.size,
                "readable": f.readable,
                "truncated": f.truncated,
                "summary": compact_summary(f),
            }
            for f in meaningful
        ],
        "inspectable_files": len(meaningful),
    }


def select_context_files(files: list[InspectedFile], max_files: int = 40, max_file_size: int = 30_000, max_total_chars: int = 60_000) -> tuple[list[tuple[str, str]], int]:
    priority_names = {
        "readme": 120, "requirements.txt": 115, "pyproject.toml": 115, "package.json": 115, "go.mod": 115,
        "pom.xml": 115, "cargo.toml": 115, "composer.json": 115, "dockerfile": 108, "compose.yml": 108,
        "docker-compose.yml": 108, "main.py": 105, "app.py": 105, "server.py": 105, "index.js": 105,
        "index.ts": 105, "src/main.py": 104,
    }
    category_weight = {
        "documentation": 90, "build/deployment": 86, "configuration": 82, "source": 78, "notebook": 72,
        "test": 60, "data/schema": 56, "markup": 50, "style": 35, "unknown text": 30,
        "asset": -20, "binary": -100, "sensitive": -1000,
    }

    def score(file: InspectedFile) -> int:
        name_score = 0
        lower_path = file.path.lower()
        base = file.path.rsplit("/", 1)[-1].lower()
        for needle, value in priority_names.items():
            if base == needle or lower_path.endswith("/" + needle):
                name_score = max(name_score, value)
        source_bonus = 10 if file.content and re.search(r"\b(class|def|function|import|from|package|func|fn)\b", file.content[:7000]) else 0
        return category_weight.get(file.category, 20) + name_score + source_bonus - min(file.size // 20000, 15)

    candidates = [f for f in files if f.readable and not f.sensitive and f.category not in {"binary", "asset"}]
    candidates.sort(key=lambda f: (-score(f), f.path))

    selected: list[tuple[str, str]] = []
    seen: set[str] = set()
    total = 0
    for file in candidates:
        if file.path in seen or len(selected) >= max_files or total >= max_total_chars:
            continue
        budget = min(max_file_size, max_total_chars - total)
        if budget < 500:
            break
        content = file.content[:budget]
        if file.truncated or len(file.content) > budget:
            content += "\n\n[FILE CONTENT TRUNCATED FOR LATENCY]"
        block = f"### FILE: {file.path}\nCATEGORY: {file.category}\nLANGUAGE: {file.language or 'unknown'}\nSIZE: {file.size} bytes\nCONTENT:\n{content}\n"
        if total + len(block) > max_total_chars:
            if total == 0:
                block = block[:max_total_chars]
            else:
                continue
        selected.append((file.path, block))
        seen.add(file.path)
        total += len(block)
    return selected, total
