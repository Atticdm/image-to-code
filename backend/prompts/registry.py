"""
Prompt registry (single place to locate prompt templates).

This module centralizes mappings from `Stack` to system prompts for different
prompt "kinds" (screenshot/text/imported-code/element-based).

Important: `prompts/__init__.py` still exposes the historical module-level
names (`SYSTEM_PROMPTS`, `TEXT_SYSTEM_PROMPTS`, `IMPORTED_CODE_SYSTEM_PROMPTS`)
because tests and other modules patch/import them directly.
"""

from __future__ import annotations

from typing import Dict, Literal

from prompts.element_based_prompts import ELEMENT_BASED_SYSTEM_PROMPTS
from prompts.imported_code_prompts import IMPORTED_CODE_SYSTEM_PROMPTS
from prompts.screenshot_system_prompts import SYSTEM_PROMPTS as SCREENSHOT_SYSTEM_PROMPTS
from prompts.text_prompts import SYSTEM_PROMPTS as TEXT_SYSTEM_PROMPTS
from prompts.types import Stack

PromptKind = Literal["screenshot", "text", "imported_code", "element_based"]


def get_system_prompt(kind: PromptKind, stack: Stack) -> str:
    if kind == "screenshot":
        return SCREENSHOT_SYSTEM_PROMPTS[stack]
    if kind == "text":
        return TEXT_SYSTEM_PROMPTS[stack]
    if kind == "imported_code":
        return IMPORTED_CODE_SYSTEM_PROMPTS[stack]
    if kind == "element_based":
        return ELEMENT_BASED_SYSTEM_PROMPTS[stack]
    raise ValueError(f"Unknown prompt kind: {kind}")


PROMPT_MAPPINGS: Dict[PromptKind, Dict[str, str]] = {
    "screenshot": SCREENSHOT_SYSTEM_PROMPTS,
    "text": TEXT_SYSTEM_PROMPTS,
    "imported_code": IMPORTED_CODE_SYSTEM_PROMPTS,
    "element_based": ELEMENT_BASED_SYSTEM_PROMPTS,
}
