from __future__ import annotations

import os
import threading
from functools import lru_cache
from typing import Iterable

MODEL_ID = os.getenv("LOCAL_MODEL_ID", "HuggingFaceTB/SmolLM2-135M-Instruct")
MAX_INPUT_TOKENS = int(os.getenv("MAX_LLM_INPUT_TOKENS", "7000"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_LLM_OUTPUT_TOKENS", "450"))

_model_lock = threading.Lock()
_model_bundle: tuple[object, object] | None = None


def model_name() -> str:
    return MODEL_ID


def dependencies_available() -> bool:
    try:
        import torch  # noqa: F401
        import transformers  # noqa: F401
        return True
    except ImportError:
        return False


def model_loaded() -> bool:
    return _model_bundle is not None


@lru_cache(maxsize=1)
def _load_model() -> tuple[object, object]:
    global _model_bundle
    with _model_lock:
        if _model_bundle is not None:
            return _model_bundle

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError(
                "Local Hugging Face inference dependencies are missing. "
                "Install the packages from requirements.txt."
            ) from exc

        # Keep CPU inference predictable on shared Streamlit Cloud runtimes.
        thread_count = max(1, min(4, os.cpu_count() or 1))
        try:
            torch.set_num_threads(thread_count)
        except RuntimeError:
            pass

        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float32,
        )
        model.eval()
        _model_bundle = (tokenizer, model)
        return _model_bundle


def generate_local(prompt: str) -> str:
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError("PyTorch is not installed in the deployment environment.") from exc

    tokenizer, model = _load_model()

    messages = [{"role": "user", "content": prompt}]
    if getattr(tokenizer, "chat_template", None):
        model_input = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
    else:
        model_input = f"User:\n{prompt}\n\nAssistant:\n"

    inputs = tokenizer(
        model_input,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_INPUT_TOKENS,
    )
    input_ids = inputs["input_ids"]

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_OUTPUT_TOKENS,
            do_sample=False,
            use_cache=True,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated = outputs[0][input_ids.shape[-1] :]
    text = tokenizer.decode(generated, skip_special_tokens=True).strip()
    if not text:
        raise RuntimeError("The local language model returned an empty explanation.")
    return text


# Backward-compatible name used by the existing backend.
class LocalLLMService:
    def __init__(self) -> None:
        self.model = MODEL_ID

    def health(self) -> bool:
        return dependencies_available()

    def generate(self, prompt: str) -> str:
        return generate_local(prompt)


def build_prompt(*, owner: str, repo_name: str, url: str, report: dict, context_blocks: Iterable[str]) -> str:
    file_lines = "\n".join(
        f"- {item['path']} | {item['category']} | {item.get('language') or 'unknown'} | {item['summary']}"
        for item in report["file_summaries"][:100]
    )
    tree = "\n".join(report["folder_tree"][:140])
    context = "\n\n".join(context_blocks)
    return f"""You are a repository code explainer for a beginner. Analyze ONLY the supplied repository evidence.
Do not invent technologies, files, databases, APIs, framework behavior, or commands. If evidence is insufficient, say so.
Binary files are metadata only. Never assume code was executed.

Repository: {owner}/{repo_name}
URL: {url}
Counts: {report['counts']}
Languages: {report['languages']}
Detected technologies (evidence-based): {report['technologies']}

FOLDER TREE:
{tree}

FILE INVENTORY:
{file_lines}

SELECTED FILE CONTENT:
{context}

Write a simple-language but technically useful explanation with exactly these headings:
## Project Overview
## Main Features / Purpose
## Main Technologies
## Repository Structure
## How It Works
## Important Files and Components
## Data Flow
## Configuration and Dependencies
## How to Run (only when supported by evidence)
## Limitations / Notes

Use only evidence from the repository. Mention when important files were truncated or when the repository is primarily documentation, configuration, data, or notebooks rather than conventional source code."""
