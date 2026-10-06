import sys
import types

import pytest

from backend import llm_service


def test_model_configuration_defaults(monkeypatch):
    monkeypatch.delenv("LOCAL_MODEL_ID", raising=False)
    assert llm_service.model_name() == "HuggingFaceTB/SmolLM2-135M-Instruct"


def test_generate_local_with_stubbed_dependencies(monkeypatch):
    class FakeTensor:
        shape = (1, 4)
        def __getitem__(self, key):
            return self

    class FakeInputs(dict):
        def __init__(self):
            super().__init__(input_ids=FakeTensor(), attention_mask=FakeTensor())

    class FakeTorch:
        class _Inference:
            def __enter__(self): return self
            def __exit__(self, *args): return False
        @staticmethod
        def inference_mode(): return FakeTorch._Inference()
        @staticmethod
        def set_num_threads(_n): pass
        float32 = object()

    class FakeTokenizer:
        chat_template = "template"
        eos_token_id = 2
        def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=True):
            return messages[0]["content"] + "\nAssistant:"
        def __call__(self, *args, **kwargs): return FakeInputs()
        def decode(self, generated, skip_special_tokens=True): return "Generated local explanation"

    class FakeModel:
        def eval(self): return self
        def generate(self, **kwargs): return FakeTensor()

    fake_transformers = types.SimpleNamespace(
        AutoTokenizer=types.SimpleNamespace(from_pretrained=lambda *_args, **_kw: FakeTokenizer()),
        AutoModelForCausalLM=types.SimpleNamespace(from_pretrained=lambda *_args, **_kw: FakeModel()),
    )
    fake_torch = types.SimpleNamespace(
        inference_mode=FakeTorch.inference_mode,
        set_num_threads=FakeTorch.set_num_threads,
        float32=FakeTorch.float32,
    )
    monkeypatch.setitem(sys.modules, "transformers", fake_transformers)
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    llm_service._model_bundle = None
    llm_service._load_model.cache_clear()

    assert llm_service.generate_local("Explain this repository.") == "Generated local explanation"

    llm_service._model_bundle = None
    llm_service._load_model.cache_clear()
