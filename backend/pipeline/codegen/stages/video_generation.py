from __future__ import annotations

from typing import Any, Callable, Coroutine, List

from openai.types.chat import ChatCompletionMessageParam

from llm import Llm
from models import stream_claude_response_native
from pipeline.types import MessageType
from prompts.claude_prompts import VIDEO_PROMPT


class VideoGenerationStage:
    """Handles video mode code generation using Claude."""

    def __init__(
        self,
        send_message: Callable[[MessageType, str, int], Coroutine[Any, Any, None]],
        throw_error: Callable[[str], Coroutine[Any, Any, None]],
    ):
        self.send_message = send_message
        self.throw_error = throw_error

    async def generate_video_code(
        self,
        prompt_messages: List[ChatCompletionMessageParam],
        anthropic_api_key: str | None,
    ) -> List[str]:
        if not anthropic_api_key:
            await self.throw_error(
                "Video only works with Anthropic models. No Anthropic API key found. "
                "Please add the environment variable ANTHROPIC_API_KEY to backend/.env "
                "or in the settings dialog"
            )
            raise Exception("No Anthropic key")

        async def process_chunk(content: str, variantIndex: int):
            await self.send_message("chunk", content, variantIndex)

        completion_results = [
            await stream_claude_response_native(
                system_prompt=VIDEO_PROMPT,
                messages=prompt_messages,  # type: ignore
                api_key=anthropic_api_key,
                callback=lambda x: process_chunk(x, 0),
                model_name=Llm.CLAUDE_3_OPUS.value,
                include_thinking=True,
            )
        ]
        completions = [result["code"] for result in completion_results]

        await self.send_message("setCode", completions[0], 0)
        await self.send_message("variantComplete", "Variant generation complete", 0)
        return completions

