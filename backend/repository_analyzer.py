"""Complete repository inventory scanner and structural tree builder."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from backend.file_inspector import (
    classify_file,
    is_sensitive_file,
    read_text_file,
)
from backend.models import CategoryCounts, FileInfo, RepositoryInventory
from backend.technology_detector import detect_technologies, LANGUAGE_BY_EXT


class RepositoryAnalyzer:
    """Scans and analyzes complete repository inventory once."""

    def __init__(self, repo_dir: Path, owner: str, repo_name: str) -> None:
        self.repo_dir = repo_dir
        self.owner = owner
        self.repo_name = repo_name

    def analyze(self) -> Tuple[RepositoryInventory, Dict[str, FileInfo]]:
        """Perform a single comprehensive inventory scan of all repository files.

        Returns:
            Tuple of (RepositoryInventory, dict mapping relative_path -> FileInfo)
        """
        category_counts = CategoryCounts()
        file_map: Dict[str, FileInfo] = {}
        manifest_contents: Dict[str, str] = {}
        language_counts: Dict[str, int] = {}
        tree_paths: List[str] = []
        sensitive_files: List[str] = []

        all_files = [
            p for p in self.repo_dir.rglob("*")
            if p.is_file() and ".git" not in p.parts
        ]

        # Sort files deterministically for consistency
        all_files.sort(key=lambda p: str(p.relative_to(self.repo_dir)))

        for file_path in all_files:
            rel_path = str(file_path.relative_to(self.repo_dir)).replace("\\", "/")
            size_bytes = file_path.stat().st_size
            ext = file_path.suffix.lower()

            tree_paths.append(rel_path)

            category = classify_file(rel_path, file_path)
            sensitive = is_sensitive_file(rel_path)

            if sensitive:
                sensitive_files.append(rel_path)

            # Update category counts
            if category == "source":
                category_counts.source += 1
            elif category == "notebook":
                category_counts.notebook += 1
            elif category == "documentation":
                category_counts.documentation += 1
            elif category == "configuration":
                category_counts.configuration += 1
            elif category == "dependency":
                category_counts.dependency += 1
            elif category == "web":
                category_counts.web += 1
            elif category == "data_schema":
                category_counts.data_schema += 1
            elif category == "test":
                category_counts.test += 1
            elif category == "deployment":
                category_counts.deployment += 1
            elif category == "binary":
                category_counts.binary += 1
            else:
                category_counts.unknown_text += 1

            # Track primary languages by extension
            if ext in LANGUAGE_BY_EXT:
                lang_name = LANGUAGE_BY_EXT[ext]
                language_counts[lang_name] = language_counts.get(lang_name, 0) + 1

            # Read dependency manifest contents for technology detection
            if category == "dependency" and not sensitive and size_bytes < 100000:
                success, text = read_text_file(file_path, max_chars=10000)
                if success:
                    manifest_contents[rel_path] = text

            file_info = FileInfo(
                path=rel_path,
                category=category,
                size_bytes=size_bytes,
                extension=ext,
                is_sensitive=sensitive,
            )
            file_map[rel_path] = file_info

        # Build technology list based on evidence
        detected_tech = detect_technologies(
            file_map={k: self.repo_dir / k for k in file_map},
            manifest_contents=manifest_contents,
            language_counts=language_counts,
        )

        # Build folder tree summary (max 60 nodes for UI display)
        tree_summary = self._build_tree_summary(tree_paths, max_nodes=60)

        # Select important files list for overview
        important_files = self._select_important_files(file_map)

        inventory = RepositoryInventory(
            owner=self.owner,
            repo_name=self.repo_name,
            total_files=len(all_files),
            category_counts=category_counts,
            languages=sorted([lang for lang, count in language_counts.items() if count > 0]),
            technologies=detected_tech,
            tree=tree_summary,
            important_files=important_files,
            sensitive_files_found=sensitive_files,
        )

        return inventory, file_map

    def _build_tree_summary(self, paths: List[str], max_nodes: int = 60) -> List[str]:
        """Convert list of relative paths into clean ASCII folder tree array."""
        if not paths:
            return ["(empty repository)"]

        display_paths = paths[:max_nodes]
        tree_lines = []

        for p in display_paths:
            parts = p.split("/")
            indent = "  " * (len(parts) - 1)
            name = parts[-1]
            prefix = "└── " if len(parts) > 1 else "├── "
            tree_lines.append(f"{indent}{prefix}{name}")

        if len(paths) > max_nodes:
            tree_lines.append(f"... and {len(paths) - max_nodes} more files")

        return tree_lines

    def _select_important_files(self, file_map: Dict[str, FileInfo]) -> List[str]:
        """Identify key files in the repository for quick inspection."""
        important = []
        priorities = ["README.md", "README", "pyproject.toml", "package.json", "app.py", "main.py", "index.js", "Dockerfile", "docker-compose.yml"]

        for prio in priorities:
            for rel_path in file_map:
                if rel_path.lower() == prio.lower() or rel_path.endswith("/" + prio):
                    if rel_path not in important:
                        important.append(rel_path)

        for rel_path, info in file_map.items():
            if len(important) >= 15:
                break
            if info.category in ("dependency", "deployment") and rel_path not in important:
                important.append(rel_path)

        return important
