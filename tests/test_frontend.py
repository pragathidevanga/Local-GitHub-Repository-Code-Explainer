from pathlib import Path


def test_streamlit_frontend_uses_embedded_backend() -> None:
    text = (Path(__file__).resolve().parents[1] / "frontend" / "app.py").read_text(encoding="utf-8")
    for marker in ["/api/analyze", "/api/jobs/", "FastAPI", "GitPython", "Hugging Face Transformers", "Streamlit"]:
        assert marker in text
    assert "ngrok" not in text.lower()
    assert "ollama" not in text.lower()
