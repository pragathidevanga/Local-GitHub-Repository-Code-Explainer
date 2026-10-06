from pathlib import Path

from backend.file_inspector import inspect_repository, summarize_counts


def make_fixture(root: Path) -> None:
    (root / "README.md").write_text("# Demo\nA Python project.", encoding="utf-8")
    (root / "main.py").write_text("import sqlite3\nclass Demo: pass\n", encoding="utf-8")
    (root / "config.yaml").write_text("model: qwen\n", encoding="utf-8")
    (root / "data.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (root / "notes.weird").write_text("function hello():\n    pass\n", encoding="utf-8")
    (root / "tests" / "test_demo.js").parent.mkdir(parents=True, exist_ok=True)
    (root / "tests" / "test_demo.js").write_text("test(\"x\", () => {})", encoding="utf-8")
    (root / ".env").write_text("SECRET=do-not-show\n", encoding="utf-8")
    (root / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00binary")
    (root / "nb.ipynb").write_text('{"cells":[{"cell_type":"markdown","source":["# Notebook"]},{"cell_type":"code","source":["print(1)"]}]}', encoding="utf-8")


def test_mixed_formats_are_classified(tmp_path: Path) -> None:
    make_fixture(tmp_path)
    files = inspect_repository(tmp_path)
    categories = {f.path: f.category for f in files}
    assert categories["README.md"] == "documentation"
    assert categories["main.py"] == "source"
    assert categories["config.yaml"] == "configuration"
    assert categories["data.csv"] == "data/schema"
    assert categories["notes.weird"] == "source"
    assert categories["image.png"] in {"binary", "asset"}
    assert categories[".env"] == "sensitive"
    assert categories["nb.ipynb"] == "notebook"
    assert categories["tests/test_demo.js"] == "test"


def test_docs_only_repo_is_not_empty(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("docs only", encoding="utf-8")
    files = inspect_repository(tmp_path)
    counts = summarize_counts(files)
    assert counts["total_files"] == 1
    assert counts["documentation_files"] == 1
