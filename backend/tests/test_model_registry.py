from models.registry import ModelRegistry
from llm import Llm


def test_registry_covers_all_models():
    for llm in Llm:
        ModelRegistry.get(llm)


def test_openai_special_cases():
    gpt5 = ModelRegistry.openai_params(Llm.GPT_5)
    assert gpt5.max_completion_tokens == 32768
    assert gpt5.temperature == 1.0

    o1 = ModelRegistry.openai_params(Llm.O1_2024_12_17)
    assert o1.supports_streaming is False
    assert o1.supports_temperature is False
    assert o1.max_completion_tokens == 20000


def test_gemini_capabilities():
    assert ModelRegistry.is_compatible(Llm.GEMINI_3_PRO, "create", "image")
    assert not ModelRegistry.is_compatible(Llm.GEMINI_3_PRO, "update", "image")
    assert not ModelRegistry.is_compatible(Llm.GEMINI_3_PRO, "create", "text")

