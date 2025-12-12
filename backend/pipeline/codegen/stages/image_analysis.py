from __future__ import annotations

from typing import Any, Callable, Coroutine, Dict, List, Tuple

from llm import Llm
from pipeline.types import MessageType
from image_analysis import extract_elements, extract_elements_as_assets


class ImageAnalysisStage:
    """Handles image analysis and element extraction."""

    def __init__(
        self,
        send_message: Callable[[MessageType, str, int], Coroutine[Any, Any, None]],
        throw_error: Callable[[str], Coroutine[Any, Any, None]],
    ):
        self.send_message = send_message
        self.throw_error = throw_error

    async def analyze_image(
        self,
        image_data_url: str,
        analysis_model: str,
        openai_api_key: str | None,
        anthropic_api_key: str | None,
        gemini_api_key: str | None,
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        try:
            await self.send_message(
                "status", "Analyzing image and extracting elements...", 0
            )

            analysis_llm = None
            for llm in Llm:
                if llm.value == analysis_model:
                    analysis_llm = llm
                    break
            if analysis_llm is None:
                raise ValueError(f"Invalid analysis model: {analysis_model}")

            await self.send_message("status", "Extracting design elements...", 0)
            elements_data = await extract_elements(
                image_data_url=image_data_url,
                analysis_model=analysis_llm,
                openai_api_key=openai_api_key,
                anthropic_api_key=anthropic_api_key,
                gemini_api_key=gemini_api_key,
            )

            await self.send_message("status", "Extracting elements as assets...", 0)
            element_assets = await extract_elements_as_assets(
                original_image_data_url=image_data_url,
                elements_data=elements_data,
            )

            await self.send_message(
                "status", f"Extracted {len(element_assets)} assets", 0
            )
            return elements_data, element_assets
        except Exception as e:
            await self.throw_error(f"Error during image analysis: {str(e)}")
            raise
