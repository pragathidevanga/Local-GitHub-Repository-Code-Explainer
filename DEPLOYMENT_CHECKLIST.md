# Streamlit Direct Deployment Checklist

## GitHub

- [ ] `app.py` is at repository root.
- [ ] `requirements.txt` is at repository root.
- [ ] Do not commit `.streamlit/secrets.toml` with secrets.
- [ ] Push to `main`.

## Streamlit Community Cloud

- [ ] Repository: your GitHub repository.
- [ ] Branch: `main`.
- [ ] Main file path: `app.py`.
- [ ] Python: `3.12`.
- [ ] No `BACKEND_URL` secret is needed.
- [ ] Deploy.

## What starts automatically

`app.py` starts the bundled FastAPI backend on `127.0.0.1:8000` inside the same runtime. The backend then runs repository processing and the local Hugging Face model.

## Expected first run

The first analysis downloads the small open-source model `HuggingFaceTB/SmolLM2-135M-Instruct`. Subsequent analyses reuse the loaded model while the Streamlit runtime remains alive.

## No external tunnel

This build does not require ngrok or any other tunnel. It also does not require a separately hosted FastAPI server or Ollama.
