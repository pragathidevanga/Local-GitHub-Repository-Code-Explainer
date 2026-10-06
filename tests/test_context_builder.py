"""Unit tests for smart context selection and character limits."""

import tempfile
from pathlib import Path

from backend.context_builder import SmartContextBuilder
from backend.repository_analyzer import RepositoryAnalyzer


def test_smart_context_prioritizes_readme_and_manifests():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        (tmp_path / "README.md").write_text("# High Priority README", encoding="utf-8")
        (tmp_path / "requirements.txt").write_text("fastapi\npydantic\n", encoding="utf-8")
        (tmp_path / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()", encoding="utf-8")
        (tmp_path / "utils.py").write_text("def helper(): return 42", encoding="utf-8")

        analyzer = RepositoryAnalyzer(tmp_path, "user", "repo")
        inventory, file_map = analyzer.analyze()

        builder = SmartContextBuilder(tmp_path, file_map)
        context = builder.build_context()

        assert context.file_count == 4
        assert context.total_characters > 0
        selected_paths = [sf.path for sf in context.selected_files]

        # README and requirements.txt should be in context
        assert "README.md" in selected_paths
        assert "requirements.txt" in selected_paths
        assert "main.py" in selected_paths


def test_sensitive_files_excluded_from_context():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        (tmp_path / ".env").write_text("SECRET_KEY=super_secret_12345", encoding="utf-8")
        (tmp_path / "app.py").write_text("print('hello')", encoding="utf-8")

        analyzer = RepositoryAnalyzer(tmp_path, "user", "repo")
        inventory, file_map = analyzer.analyze()

        builder = SmartContextBuilder(tmp_path, file_map)
        context = builder.build_context()

        selected_paths = [sf.path for sf in context.selected_files]
        assert ".env" not in selected_paths
        assert "app.py" in selected_paths
