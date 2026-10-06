"""Single-file Streamlit deployment entrypoint.

Run locally or on Streamlit Community Cloud with:
    streamlit run app.py

The app starts the bundled FastAPI backend inside the same runtime and uses a small
open-source Hugging Face model for local inference. No ngrok, FastAPI cloud host,
Ollama server, or external LLM endpoint is required.
"""

from __future__ import annotations

import streamlit as st

from backend.local_server import start_embedded_fastapi


@st.cache_resource(show_spinner=False)
def start_backend_once() -> tuple[str, bool]:
    return start_embedded_fastapi()


BACKEND_URL, BACKEND_READY = start_backend_once()

# Import only after the backend URL is fixed.
from frontend.app import main  # noqa: E402


if __name__ == "__main__":
    main(local_backend_ready=BACKEND_READY)
