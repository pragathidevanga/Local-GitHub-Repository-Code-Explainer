# Local GitHub Repository Code Explainer

A Streamlit-deployable GenAI application that accepts **any public HTTPS GitHub repository URL**, inspects its contents, and generates a beginner-friendly explanation using a small open-source Hugging Face model running locally inside the Streamlit runtime.

## Pipeline

**GitHub Repository → GitPython → Repository Analyzer → Smart Context → Local Transformers Model → FastAPI → Streamlit → Explanation**

The FastAPI backend is started **inside the same Streamlit runtime**, so the deployed app does not need ngrok, an external FastAPI server, Ollama, or a second cloud service.

## Assignment requirements covered

- Accepts public GitHub repository URLs from any owner.
- Shallow-clones repositories with GitPython (with a safe public-archive fallback when a Git executable is unavailable).
- Dynamically inventories source code, notebooks, README/docs, configuration, data/schema, tests, markup, styles, deployment files, readable text, assets, and binary files.
- Jupyter notebooks are parsed without executing them.
- Sensitive files are withheld from model context.
- The complete repository is inventoried; only relevant evidence is sent to the model to reduce latency.
- A real local open-source LLM generates the final explanation. The default model is `HuggingFaceTB/SmolLM2-135M-Instruct`, a public Apache-2.0 model whose Hugging Face model card provides Transformers usage instructions. The model weights are about 269 MB. citeturn880204search0turn880204search2
- FastAPI, Pydantic and Uvicorn provide the backend API.
- Streamlit provides the frontend.
- No hard-coded explanation is used.

## Deploy directly on Streamlit Community Cloud

1. Upload the project contents to a GitHub repository.
2. In Streamlit Community Cloud choose the repository and branch `main`.
3. Set **Main file path** to `app.py`.
4. Use Python 3.12 in Advanced settings.
5. Do **not** add a `BACKEND_URL` secret. The backend is embedded in the app runtime.
6. Deploy.

Streamlit Community Cloud deploys from GitHub and lets you choose the repository, branch, entrypoint file, Python version and secrets. citeturn880204search4

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app starts its FastAPI server automatically on `127.0.0.1:8000`.

## Local model

The default model is:

```text
HuggingFaceTB/SmolLM2-135M-Instruct
```

It is downloaded from Hugging Face on first analysis and then reused from the runtime cache. No API key is required for this public model.

For a different small public Transformers model, set `LOCAL_MODEL_ID` before starting the app.

## Performance design

The application keeps the complete repository inventory but limits the model context to the most relevant evidence. Large readable files are truncated, binary files are metadata-only, and the model input/output token budgets are bounded. The API uses background jobs and polling so the Streamlit request is not held open while repository analysis runs.

## Security

- Only public HTTPS GitHub repositories are accepted.
- Repository code and notebooks are never executed.
- Sensitive files such as secrets and private keys are not sent to the model.
- Archive extraction checks for unsafe paths.

## Important deployment note

The term "local model" here means the model is executed locally **inside the Streamlit deployment runtime** using Transformers and PyTorch. It is not an external hosted LLM API.
