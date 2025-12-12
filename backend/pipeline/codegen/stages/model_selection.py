from __future__ import annotations

from typing import Callable, Coroutine, List, Literal

from config import NUM_VARIANTS
from custom_types import InputMode
from llm import Llm
from models.registry import ModelRegistry


class ModelSelectionStage:
    """Selects variant models based on available API keys and preference."""

    def __init__(self, throw_error: Callable[[str], Coroutine[Any, Any, None]]):
        self.throw_error = throw_error

    async def select_models(
        self,
        generation_type: Literal["create", "update"],
        input_mode: InputMode,
        openai_api_key: str | None,
        anthropic_api_key: str | None,
        gemini_api_key: str | None = None,
        preferred_model: str | None = None,
    ) -> List[Llm]:
        try:
            models = self._get_variant_models(
                generation_type,
                input_mode,
                NUM_VARIANTS,
                openai_api_key,
                anthropic_api_key,
                gemini_api_key,
                preferred_model,
            )
            print("Variant models:")
            for index, model in enumerate(models):
                print(f"Variant {index + 1}: {model.value}")
            return models
        except Exception:
            await self.throw_error(
                "No OpenAI or Anthropic API key found. Please add the environment variable "
                "OPENAI_API_KEY or ANTHROPIC_API_KEY to backend/.env or in the settings dialog. "
                "If you add it to .env, make sure to restart the backend server."
            )
            raise Exception("No OpenAI or Anthropic key")

    def _get_variant_models(
        self,
        generation_type: Literal["create", "update"],
        input_mode: InputMode,
        num_variants: int,
        openai_api_key: str | None,
        anthropic_api_key: str | None,
        gemini_api_key: str | None,
        preferred_model: str | None,
    ) -> List[Llm]:
        preferred_llm: Llm | None = None
        if preferred_model:
            for llm in Llm:
                if llm.value == preferred_model:
                    preferred_llm = llm
                    break

        def provider_available(llm: Llm) -> bool:
            provider = ModelRegistry.provider(llm)
            if provider == "openai":
                return bool(openai_api_key)
            if provider == "anthropic":
                return bool(anthropic_api_key)
            if provider == "gemini":
                return bool(gemini_api_key)
            return False

        if (
            preferred_llm
            and provider_available(preferred_llm)
            and ModelRegistry.is_compatible(preferred_llm, generation_type, input_mode)
        ):
            return [preferred_llm for _ in range(num_variants)]

        chosen: Llm | None = None
        if openai_api_key:
            candidate = ModelRegistry.latest_for_provider("openai")
            if ModelRegistry.is_compatible(candidate, generation_type, input_mode):
                chosen = candidate
        if chosen is None and anthropic_api_key:
            candidate = ModelRegistry.latest_for_provider("anthropic")
            if ModelRegistry.is_compatible(candidate, generation_type, input_mode):
                chosen = candidate
        if chosen is None and gemini_api_key:
            candidate = ModelRegistry.latest_for_provider("gemini")
            if ModelRegistry.is_compatible(candidate, generation_type, input_mode):
                chosen = candidate

        if chosen is None:
            raise Exception("No OpenAI or Anthropic key")

        return [chosen for _ in range(num_variants)]

