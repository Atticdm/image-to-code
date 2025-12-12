from __future__ import annotations

from typing import List

from fastapi import WebSocket
from openai.types.chat import ChatCompletionMessageParam

from codegen.utils import extract_html_content
from fs_logging.core import write_logs


class PostProcessingStage:
    """Handles post-processing after code generation completes."""

    async def process_completions(
        self,
        completions: List[str],
        prompt_messages: List[ChatCompletionMessageParam],
        websocket: WebSocket,
    ) -> None:
        valid_completions = [comp for comp in completions if comp]
        if valid_completions:
            html_content = extract_html_content(valid_completions[0])
            write_logs(prompt_messages, html_content)

