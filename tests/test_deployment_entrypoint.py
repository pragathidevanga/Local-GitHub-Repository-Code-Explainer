from pathlib import Path


def test_root_streamlit_entrypoint_is_deployable() -> None:
    app = Path(__file__).resolve().parents[1] / "app.py"
    requirements = app.parent / "requirements.txt"
    assert app.exists()
    assert requirements.exists()
    text = app.read_text(encoding="utf-8")
    assert "streamlit" in text
    assert "start_backend_once" in text
