from __future__ import annotations

from typing import Any, Callable, Coroutine, List

from custom_types import InputMode
from mock_llm import mock_completion
from pipeline.types import MessageType


class MockResponseStage:
    """Handles mock AI responses for testing."""

    def __init__(
        self,
        send_message: Callable[[MessageType, str, int], Coroutine[Any, Any, None]],
    ):
        self.send_message = send_message

    async def generate_mock_response(self, input_mode: InputMode) -> List[str]:
        async def process_chunk(content: str, variantIndex: int):
            await self.send_message("chunk", content, variantIndex)

        completion_results = [
            await mock_completion(process_chunk, input_mode=input_mode)
        ]
        completions = [result["code"] for result in completion_results]

        await self.send_message("setCode", completions[0], 0)
        await self.send_message("variantComplete", "Variant generation complete", 0)
        return completions

