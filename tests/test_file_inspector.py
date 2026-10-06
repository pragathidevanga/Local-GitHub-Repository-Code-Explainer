"""Unit tests for file inspection, sensitive file protection, binary detection, and notebook parsing."""

import json
import tempfile
from pathlib import Path

from backend.file_inspector import (
    classify_file,
    is_binary_file,
    is_sensitive_file,
    parse_jupyter_notebook,
    read_text_file,
)


def test_sensitive_file_detection():
    assert is_sensitive_file(".env") is True
    assert is_sensitive_file(".env.local") is True
    assert is_sensitive_file("id_rsa") is True
    assert is_sensitive_file("server.key") is True
    assert is_sensitive_file("app.py") is False


def test_binary_file_detection():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Text file
        txt_file = tmp_path / "hello.txt"
        txt_file.write_text("Hello World", encoding="utf-8")
        assert is_binary_file(txt_file) is False

        # Binary file with null byte
        bin_file = tmp_path / "data.bin"
        bin_file.write_bytes(b"\x00\x01\x02\x03\x04")
        assert is_binary_file(bin_file) is True


def test_classify_file():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        py_file = tmp_path / "main.py"
        py_file.write_text("print('hello')", encoding="utf-8")
        assert classify_file("main.py", py_file) == "source"

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("streamlit\nfastapi\n", encoding="utf-8")
        assert classify_file("requirements.txt", req_file) == "dependency"

        docker_file = tmp_path / "Dockerfile"
        docker_file.write_text("FROM python:3.10", encoding="utf-8")
        assert classify_file("Dockerfile", docker_file) == "deployment"

        readme_file = tmp_path / "README.md"
        readme_file.write_text("# Project", encoding="utf-8")
        assert classify_file("README.md", readme_file) == "documentation"


def test_parse_jupyter_notebook():
    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["# Analysis Notebook\n", "This notebook analyzes data."]
            },
            {
                "cell_type": "code",
                "source": ["import pandas as pd\n", "df = pd.DataFrame({'a': [1, 2]})"],
                "outputs": [{"output_type": "stream", "text": ["huge output data..."]}]
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 2
    }

    with tempfile.TemporaryDirectory() as tmp_dir:
        nb_path = Path(tmp_dir) / "test.ipynb"
        nb_path.write_text(json.dumps(notebook_content), encoding="utf-8")

        parsed = parse_jupyter_notebook(nb_path)
        assert "# Analysis Notebook" in parsed
        assert "import pandas as pd" in parsed
        assert "huge output data..." not in parsed  # Outputs are ignored
