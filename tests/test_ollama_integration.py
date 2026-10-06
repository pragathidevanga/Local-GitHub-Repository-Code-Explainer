"""Integration tests for local Ollama and Qwen 2.5 3B."""

import pytest
from backend.llm_service import check_ollama_status, generate_with_ollama_local


def test_ollama_status_check():
    status = check_ollama_status()
    assert isinstance(status.connected, bool)
    assert isinstance(status.model_available, bool)
    assert status.model_name == "qwen2.5:3b"


def test_real_qwen_inference_if_available():
    status = check_ollama_status()
    if status.connected and status.model_available:
        success, explanation = generate_with_ollama_local(
            prompt="Say hello in 5 words."
        )
        assert success is True
        assert len(explanation) > 0
    else:
        pytest.skip("Local Ollama or qwen2.5:3b is not available in test environment.")
