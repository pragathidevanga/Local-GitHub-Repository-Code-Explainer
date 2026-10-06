# Direct Streamlit Deployment

This project is intentionally packaged so the only Streamlit entrypoint is:

```bash
streamlit run app.py
```

For Streamlit Community Cloud, set the main file path to:

```text
app.py
```

No `BACKEND_URL` secret is required. `app.py` starts FastAPI inside the same runtime, and FastAPI uses the local Hugging Face Transformers model.

The model is `HuggingFaceTB/SmolLM2-135M-Instruct`. Its Hugging Face model card documents direct Transformers usage, and the published `model.safetensors` is about 269 MB. citeturn880204search0turn880204search2

Streamlit Community Cloud supports deployment from GitHub and lets you choose the entrypoint and Python version in the deployment dialog. citeturn880204search4
