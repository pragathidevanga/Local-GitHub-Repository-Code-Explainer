"""Unit tests for evidence-based Qwen prompt builder."""

import tempfile
from pathlib import Path

from backend.context_builder import SmartContextBuilder
from backend.llm_service import build_qwen_prompt
from backend.repository_analyzer import RepositoryAnalyzer


def test_build_qwen_prompt_contains_all_sections():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        (tmp_path / "README.md").write_text("# Demo Repository\nExplanations demo.", encoding="utf-8")
        (tmp_path / "app.py").write_text("import streamlit as st\nst.write('App')", encoding="utf-8")

        analyzer = RepositoryAnalyzer(tmp_path, "demo_owner", "demo_repo")
        inventory, file_map = analyzer.analyze()

        builder = SmartContextBuilder(tmp_path, file_map)
        context = builder.build_context()

        prompt = build_qwen_prompt(inventory, context)

        assert "You are an expert AI software architect" in prompt
        assert "Repository Owner: demo_owner" in prompt
        assert "Repository Name: demo_repo" in prompt
        assert "1. Project Overview" in prompt
        assert "5. Important Files" in prompt
        assert "7. Application Architecture" in prompt
        assert "10. Data Flow" in prompt
        assert "23. Limitations / Unknown Information" in prompt
