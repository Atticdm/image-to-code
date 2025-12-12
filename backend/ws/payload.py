"""
WebSocket payload schema for `/generate-code`.

Frontend sends `FullGenerationSettings` = `CodeGenerationParams & Settings`
from `frontend/src/types.ts`. This module is the single source of truth on
the backend for:
  - field names
  - their types
  - intended meaning

Fields:
  Generation params:
    - generationType: "create" | "update"
      Create a new version from prompt, or update based on history.
    - inputMode: "image" | "video" | "text"
      Determines prompt assembly and which generation flow runs.
    - prompt: { text, images }
      Primary prompt content. For image/video, images[0] is a data URL.
    - history: PromptContent[]
      Alternating assistant/user messages for update flow.
    - isImportedFromCode: bool
      If true, history[0].text is treated as imported baseline code.

  Settings (merged into WS payload by frontend):
    - generatedCodeConfig: stack name (see prompts.types.Stack)
    - codeGenerationModel: preferred model id (string from frontend dropdown)
      Used as preference for provider/model selection.
    - analysisModel: model id used for element extraction (optional)
    - openAiApiKey / anthropicApiKey / geminiApiKey / openAiBaseURL: provider config
    - isImageGenerationEnabled: whether to replace placeholders with generated images
    - screenshotOneApiKey / editorTheme / isTermOfServiceAccepted:
      Frontend settings, currently ignored by this route but allowed for
      forwards compatibility.
"""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from custom_types import InputMode
from prompts.types import Stack


class WsPromptContent(BaseModel):
    """Prompt text plus optional images (data URLs)."""

    text: str = ""
    images: List[str] = Field(default_factory=list)


class GenerateCodeWsPayload(BaseModel):
    """Typed WS request payload for `/generate-code`."""

    # Generation params
    generationType: Literal["create", "update"] = "create"
    inputMode: InputMode = "image"
    prompt: WsPromptContent = Field(default_factory=WsPromptContent)
    history: List[WsPromptContent] = Field(default_factory=list)
    isImportedFromCode: bool = False

    # Settings
    openAiApiKey: Optional[str] = None
    openAiBaseURL: Optional[str] = None
    anthropicApiKey: Optional[str] = None
    geminiApiKey: Optional[str] = None
    screenshotOneApiKey: Optional[str] = None
    isImageGenerationEnabled: bool = True
    editorTheme: Optional[str] = None
    generatedCodeConfig: Stack = "html_tailwind"
    codeGenerationModel: Optional[str] = None
    analysisModel: Optional[str] = None
    isTermOfServiceAccepted: Optional[bool] = None

    # Accept unknown fields to avoid breaking older/newer frontends.
    model_config = ConfigDict(extra="allow")

