"""Smart context builder for low-latency LLM model prompt construction."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from backend.code_extractor import excerpt_large_file
from backend.file_inspector import parse_jupyter_notebook, read_text_file
from backend.models import FileInfo, SelectedFileContext, SmartContext

MAX_TOTAL_CONTEXT_CHARS = 38000
MAX_FILES_FOR_LLM = 25
MAX_FILE_SIZE_CHARS = 22000

ENTRY_POINT_FILENAMES = {
    "app.py", "main.py", "index.js", "server.js", "index.ts", "server.ts",
    "main.go", "main.rs", "app.java", "mainactivity.java", "application.java",
    "manage.py", "wsgi.py", "asgi.py", "cli.py", "run.py",
}


def compute_file_priority(rel_path: str, info: FileInfo) -> int:
    """Compute dynamic priority score for model context selection (higher is selected first)."""
    if info.is_sensitive or info.category == "binary":
        return -100

    name_lower = Path(rel_path).name.lower()
    rel_lower = rel_path.lower()

    # 1. README / Main docs (Highest)
    if name_lower.startswith("readme"):
        return 100

    # 2. Dependency manifests
    if info.category == "dependency":
        return 90

    # 3. Configuration & Deployment
    if info.category in ("configuration", "deployment"):
        return 85

    # 4. Entry points
    if name_lower in ENTRY_POINT_FILENAMES:
        return 80

    # 5. Core Source code
    if info.category == "source":
        # Boost top-level or main package files over deep utilities
        depth = len(rel_path.split("/"))
        return max(75 - depth * 3, 50)

    # 6. Notebooks
    if info.category == "notebook":
        return 65

    # 7. Tests
    if info.category == "test":
        return 60

    # 8. Web / HTML / CSS
    if info.category == "web":
        return 55

    # 9. Data & Schema
    if info.category == "data_schema":
        return 50

    # 10. Documentation
    if info.category == "documentation":
        return 45

    return 30


class SmartContextBuilder:
    """Selects top relevant repository files within strict character and file counts."""

    def __init__(self, repo_dir: Path, file_map: Dict[str, FileInfo]) -> None:
        self.repo_dir = repo_dir
        self.file_map = file_map

    def build_context(self) -> SmartContext:
        """Construct smart context from pre-scanned file inventory."""
        scored_files: List[Tuple[int, str, FileInfo]] = []

        for rel_path, info in self.file_map.items():
            score = compute_file_priority(rel_path, info)
            if score > 0:
                scored_files.append((score, rel_path, info))

        # Sort by score descending, then by path
        scored_files.sort(key=lambda x: (-x[0], x[1]))

        selected_files: List[SelectedFileContext] = []
        total_chars = 0

        for score, rel_path, info in scored_files:
            if len(selected_files) >= MAX_FILES_FOR_LLM:
                break
            if total_chars >= MAX_TOTAL_CONTEXT_CHARS:
                break

            file_path = self.repo_dir / rel_path

            if info.category == "notebook":
                raw_text = parse_jupyter_notebook(file_path)
                success = True
            else:
                success, raw_text = read_text_file(file_path, max_chars=50000)

            if not success or not raw_text.strip():
                continue

            # Excerpt large content smartly
            content, is_truncated = excerpt_large_file(raw_text, max_chars=MAX_FILE_SIZE_CHARS)
            char_count = len(content)

            # Check if adding this file exceeds character budget
            if total_chars + char_count > MAX_TOTAL_CONTEXT_CHARS:
                # If budget is tight, try taking a smaller slice of at least 2000 chars
                remaining_budget = MAX_TOTAL_CONTEXT_CHARS - total_chars
                if remaining_budget < 1500:
                    break
                content = content[:remaining_budget] + "\n... [TRUNCATED DUE TO CONTEXT BUDGET] ..."
                char_count = len(content)
                is_truncated = True

            selected_files.append(
                SelectedFileContext(
                    path=rel_path,
                    category=info.category,
                    character_count=char_count,
                    is_truncated=is_truncated,
                    content=content,
                )
            )
            total_chars += char_count

        return SmartContext(
            selected_files=selected_files,
            total_characters=total_chars,
            file_count=len(selected_files),
        )
