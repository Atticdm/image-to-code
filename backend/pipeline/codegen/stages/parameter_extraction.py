from __future__ import annotations

from typing import Any, Callable, Coroutine, Dict, List, Literal, cast

from pydantic import ValidationError

from config import (
    ANTHROPIC_API_KEY,
    GEMINI_API_KEY,
    IS_PROD,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
)
from custom_types import InputMode
from pipeline.codegen.context import ExtractedParams
from prompts.types import PromptContent
from ws.payload import GenerateCodeWsPayload


class ParameterExtractionStage:
    """Handles parameter extraction and validation from WebSocket requests."""

    def __init__(self, throw_error: Callable[[str], Coroutine[Any, Any, None]]):
        self.throw_error = throw_error

    async def extract_and_validate(self, params: Dict[str, Any]) -> ExtractedParams:
        try:
            payload = GenerateCodeWsPayload.model_validate(params)
        except ValidationError as e:
            await self.throw_error(f"Invalid request payload: {e}")
            raise

        validated_stack = payload.generatedCodeConfig
        validated_input_mode = payload.inputMode

        openai_api_key = self._get_from_settings_dialog_or_env(
            params, "openAiApiKey", OPENAI_API_KEY
        )
        anthropic_api_key = self._get_from_settings_dialog_or_env(
            params, "anthropicApiKey", ANTHROPIC_API_KEY
        )
        gemini_api_key = self._get_from_settings_dialog_or_env(
            params, "geminiApiKey", GEMINI_API_KEY
        )

        openai_base_url: str | None = None
        if not IS_PROD:
            openai_base_url = self._get_from_settings_dialog_or_env(
                params, "openAiBaseURL", OPENAI_BASE_URL
            )
        if not openai_base_url:
            print("Using official OpenAI URL")

        should_generate_images = payload.isImageGenerationEnabled
        generation_type: Literal["create", "update"] = payload.generationType
        prompt = cast(PromptContent, payload.prompt.model_dump())
        history = [h.model_dump() for h in payload.history]
        is_imported_from_code = payload.isImportedFromCode
        code_generation_model = payload.codeGenerationModel
        analysis_model = payload.analysisModel

        use_element_extraction = (
            analysis_model is not None
            and validated_input_mode == "image"
            and generation_type == "create"
        )

        return ExtractedParams(
            stack=validated_stack,
            input_mode=validated_input_mode,
            should_generate_images=should_generate_images,
            openai_api_key=openai_api_key,
            anthropic_api_key=anthropic_api_key,
            gemini_api_key=gemini_api_key,
            openai_base_url=openai_base_url,
            generation_type=generation_type,
            prompt=prompt,
            history=history,
            is_imported_from_code=is_imported_from_code,
            code_generation_model=code_generation_model,
            analysis_model=analysis_model,
            use_element_extraction=use_element_extraction,
        )

    def _get_from_settings_dialog_or_env(
        self, params: dict[str, Any], key: str, env_var: str | None
    ) -> str | None:
        value = params.get(key)
        if isinstance(value, str) and value:
            print(f"Using {key} from client-side settings dialog")
            return value
        if env_var:
            print(f"Using {key} from environment variable")
            return env_var
        return None

