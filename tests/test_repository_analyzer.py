"""Unit tests for complete repository inventory scanner."""

import tempfile
from pathlib import Path

from backend.repository_analyzer import RepositoryAnalyzer


def test_repository_inventory_scanning():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Create mock repository files
        (tmp_path / "README.md").write_text("# Test Project", encoding="utf-8")
        (tmp_path / "app.py").write_text("import streamlit as st\nst.write('hi')", encoding="utf-8")
        (tmp_path / "requirements.txt").write_text("streamlit\nfastapi\n", encoding="utf-8")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "guide.md").write_text("Documentation guide", encoding="utf-8")

        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_app.py").write_text("def test_one(): assert True", encoding="utf-8")

        analyzer = RepositoryAnalyzer(tmp_path, "test_owner", "test_repo")
        inventory, file_map = analyzer.analyze()

        assert inventory.owner == "test_owner"
        assert inventory.repo_name == "test_repo"
        assert inventory.total_files == 5
        assert inventory.category_counts.documentation >= 2
        assert inventory.category_counts.source >= 1
        assert inventory.category_counts.dependency == 1
        assert inventory.category_counts.test == 1
        assert "Python" in inventory.languages
        assert "Streamlit" in inventory.technologies
        assert len(inventory.tree) >= 5


def test_readme_only_repository():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        (tmp_path / "README.md").write_text("# Documentation Only Repo", encoding="utf-8")

        analyzer = RepositoryAnalyzer(tmp_path, "docs_user", "docs_repo")
        inventory, file_map = analyzer.analyze()

        assert inventory.total_files == 1
        assert inventory.category_counts.documentation == 1
        assert inventory.category_counts.source == 0
        # Must NOT be considered empty
        assert len(file_map) == 1
