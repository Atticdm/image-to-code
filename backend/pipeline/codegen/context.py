from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal

from fastapi import WebSocket
from openai.types.chat import ChatCompletionMessageParam

from custom_types import InputMode
from llm import Llm
from pipeline.ws import WebSocketCommunicator
from prompts.types import PromptContent, Stack


class VariantErrorAlreadySent(Exception):
    """Indicates a variantError message has already been sent to frontend."""

    def __init__(self, original_error: Exception):
        self.original_error = original_error
        super().__init__(str(original_error))


@dataclass
class PipelineContext:
    """Context object that carries state through the pipeline."""

    websocket: WebSocket
    ws_comm: WebSocketCommunicator | None = None
    params: Dict[str, Any] = field(default_factory=dict)
    extracted_params: "ExtractedParams | None" = None
    prompt_messages: List[ChatCompletionMessageParam] = field(default_factory=list)
    image_cache: Dict[str, str] = field(default_factory=dict)
    variant_models: List[Llm] = field(default_factory=list)
    completions: List[str] = field(default_factory=list)
    variant_completions: Dict[int, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_elements: Dict[str, Any] | None = None
    element_assets: Dict[str, str] = field(default_factory=dict)

    @property
    def send_message(self):
        assert self.ws_comm is not None
        return self.ws_comm.send_message

    @property
    def throw_error(self):
        assert self.ws_comm is not None
        return self.ws_comm.throw_error


@dataclass
class ExtractedParams:
    stack: Stack
    input_mode: InputMode
    should_generate_images: bool
    openai_api_key: str | None
    anthropic_api_key: str | None
    gemini_api_key: str | None
    openai_base_url: str | None
    generation_type: Literal["create", "update"]
    prompt: PromptContent
    history: List[Dict[str, Any]]
    is_imported_from_code: bool
    code_generation_model: str | None = None
    analysis_model: str | None = None
    use_element_extraction: bool = False
