import pytest
from unittest.mock import AsyncMock

from pipeline.codegen.stages.model_selection import ModelSelectionStage
from config import NUM_VARIANTS
from llm import Llm


class TestModelSelectionPreference:
    """Model selection honors user preference with fallbacks."""

    def setup_method(self):
        mock_throw_error = AsyncMock()
        self.model_selector = ModelSelectionStage(mock_throw_error)

    @pytest.mark.asyncio
    async def test_preferred_openai_used_when_key_present(self):
        models = await self.model_selector.select_models(
            generation_type="create",
            input_mode="text",
            openai_api_key="key",
            anthropic_api_key="key",
            gemini_api_key="key",
            preferred_model=Llm.GPT_5.value,
        )
        assert models == [Llm.GPT_5] * NUM_VARIANTS

    @pytest.mark.asyncio
    async def test_preferred_anthropic_used_when_key_present(self):
        models = await self.model_selector.select_models(
            generation_type="create",
            input_mode="image",
            openai_api_key="key",
            anthropic_api_key="key",
            gemini_api_key="key",
            preferred_model=Llm.CLAUDE_4_5_SONNET_2025_11_01.value,
        )
        assert models == [Llm.CLAUDE_4_5_SONNET_2025_11_01] * NUM_VARIANTS

    @pytest.mark.asyncio
    async def test_preferred_gemini_used_for_image_create(self):
        models = await self.model_selector.select_models(
            generation_type="create",
            input_mode="image",
            openai_api_key="key",
            anthropic_api_key="key",
            gemini_api_key="key",
            preferred_model=Llm.GEMINI_3_PRO.value,
        )
        assert models == [Llm.GEMINI_3_PRO] * NUM_VARIANTS

    @pytest.mark.asyncio
    async def test_gemini_preference_falls_back_on_update(self):
        models = await self.model_selector.select_models(
            generation_type="update",
            input_mode="image",
            openai_api_key="key",
            anthropic_api_key="key",
            gemini_api_key="key",
            preferred_model=Llm.GEMINI_3_PRO.value,
        )
        assert models == [Llm.GPT_5] * NUM_VARIANTS

    @pytest.mark.asyncio
    async def test_openai_preference_falls_back_when_key_missing(self):
        models = await self.model_selector.select_models(
            generation_type="create",
            input_mode="text",
            openai_api_key=None,
            anthropic_api_key="key",
            gemini_api_key="key",
            preferred_model=Llm.GPT_5.value,
        )
        assert models == [Llm.CLAUDE_4_5_OPUS_2025_11_01] * NUM_VARIANTS

    @pytest.mark.asyncio
    async def test_invalid_preference_uses_default_fallback_order(self):
        models = await self.model_selector.select_models(
            generation_type="create",
            input_mode="text",
            openai_api_key="key",
            anthropic_api_key="key",
            gemini_api_key="key",
            preferred_model="not-a-real-model",
        )
        assert models == [Llm.GPT_5] * NUM_VARIANTS
