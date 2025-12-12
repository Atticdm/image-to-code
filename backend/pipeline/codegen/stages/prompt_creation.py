from __future__ import annotations

import json
from typing import Any, Callable, Coroutine, Dict, List

from openai.types.chat import ChatCompletionMessageParam

from pipeline.codegen.context import ExtractedParams
from prompts import create_prompt
from prompts.registry import ELEMENT_BASED_SYSTEM_PROMPTS
from utils import print_prompt_summary


class PromptCreationStage:
    """Handles prompt assembly for code generation."""

    def __init__(self, throw_error: Callable[[str], Coroutine[Any, Any, None]]):
        self.throw_error = throw_error

    async def create_prompt(
        self,
        extracted_params: ExtractedParams,
        elements_data: Dict[str, Any] | None = None,
        element_assets: Dict[str, str] | None = None,
    ) -> tuple[List[ChatCompletionMessageParam], Dict[str, str]]:
        try:
            if (
                extracted_params.use_element_extraction
                and elements_data
                and element_assets
            ):
                return await self.create_prompt_with_elements(
                    extracted_params, elements_data, element_assets
                )

            prompt_messages, image_cache = await create_prompt(
                stack=extracted_params.stack,
                input_mode=extracted_params.input_mode,
                generation_type=extracted_params.generation_type,
                prompt=extracted_params.prompt,
                history=extracted_params.history,
                is_imported_from_code=extracted_params.is_imported_from_code,
            )

            print_prompt_summary(prompt_messages, truncate=False)
            return prompt_messages, image_cache
        except Exception:
            await self.throw_error(
                "Error assembling prompt. Contact support at support@picoapps.xyz"
            )
            raise

    async def create_prompt_with_elements(
        self,
        extracted_params: ExtractedParams,
        elements_data: Dict[str, Any],
        element_assets: Dict[str, str],
    ) -> tuple[List[ChatCompletionMessageParam], Dict[str, str]]:
        stack = extracted_params.stack
        system_content = ELEMENT_BASED_SYSTEM_PROMPTS[stack]

        elements_info = json.dumps(
            {
                "elements": elements_data.get("elements", []),
                "image_dimensions": elements_data.get("image_dimensions", {}),
            },
            indent=2,
        )

        image_url = extracted_params.prompt["images"][0]
        user_content: List[Any] = [
            {
                "type": "image_url",
                "image_url": {"url": image_url, "detail": "high"},
            },
            {
                "type": "text",
                "text": f"""Generate code using the extracted design elements.

Extracted elements data:
{elements_info}

For each NON-TEXT element in the extracted elements list:
- Render it as an <img> with an exact-positioned wrapper (or CSS absolute layout)
- Use this placeholder format EXACTLY so the backend can inject the real asset pixels:
  <img src="https://placehold.co/{{WIDTH}}x{{HEIGHT}}" alt="{{element_id}}" />
- Do NOT change the element_id in the alt attribute.
- You may add data-prompt="short description" for optional image generation fallback.
Place elements at their exact coordinates from the extracted elements data.
Match colors, fonts, sizes, spacing EXACTLY as shown in the screenshot.
""",
            },
        ]

        prompt_messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]

        print_prompt_summary(prompt_messages, truncate=False)
        return prompt_messages, element_assets
