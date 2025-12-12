from __future__ import annotations

from typing import Dict, List, Literal, Optional, Set

from fastapi import APIRouter
from pydantic import BaseModel

from llm import Llm
from models.registry import ModelRegistry, Provider
from prompts.types import Stack


router = APIRouter()


class PublicModelInfo(BaseModel):
    id: str
    name: str
    provider: Provider
    supports_input_modes: List[str]
    supports_generation_types: List[str]


class PublicStackInfo(BaseModel):
    id: str
    label: str
    components: List[str]
    in_beta: bool = False


class ModelsResponse(BaseModel):
    models: List[PublicModelInfo]
    stacks: List[PublicStackInfo]
    defaults: Dict[str, Optional[str]]
    recommended: Dict[str, List[str]]


def _model_display_name(llm: Llm) -> str:
    explicit = {
        Llm.GPT_5: "GPT-5",
        Llm.GPT_5_TURBO: "GPT-5 Turbo",
        Llm.GPT_4_1_2025_04_14: "GPT-4.1",
        Llm.GPT_4O_2024_11_20: "GPT-4o",
        Llm.CLAUDE_4_5_OPUS_2025_11_01: "Claude Opus 4.5",
        Llm.CLAUDE_4_5_SONNET_2025_11_01: "Claude Sonnet 4.5",
        Llm.GEMINI_3_PRO: "Gemini 3 Pro",
        Llm.GEMINI_3_PRO_NANO: "Gemini 3 Pro Nano",
    }
    if llm in explicit:
        return explicit[llm]

    v = llm.value
    if v.startswith("claude-"):
        return v.replace("-", " ").title()
    if v.startswith("gemini-"):
        return v.replace("-", " ").title()
    if v.startswith("gpt-"):
        return v.replace("-", " ").upper().replace("GPT ", "GPT-")
    return v


def _stack_info(stack: Stack) -> PublicStackInfo:
    # Keep this minimal and stable for frontend display.
    mapping: Dict[Stack, PublicStackInfo] = {
        "html_css": PublicStackInfo(
            id="html_css", label="HTML + CSS", components=["HTML", "CSS"], in_beta=False
        ),
        "html_tailwind": PublicStackInfo(
            id="html_tailwind",
            label="HTML + Tailwind",
            components=["HTML", "Tailwind"],
            in_beta=False,
        ),
        "react_tailwind": PublicStackInfo(
            id="react_tailwind",
            label="React + Tailwind",
            components=["React", "Tailwind"],
            in_beta=False,
        ),
        "bootstrap": PublicStackInfo(
            id="bootstrap", label="Bootstrap", components=["Bootstrap"], in_beta=False
        ),
        "vue_tailwind": PublicStackInfo(
            id="vue_tailwind",
            label="Vue + Tailwind",
            components=["Vue", "Tailwind"],
            in_beta=True,
        ),
        "ionic_tailwind": PublicStackInfo(
            id="ionic_tailwind",
            label="Ionic + Tailwind",
            components=["Ionic", "Tailwind"],
            in_beta=True,
        ),
        "svg": PublicStackInfo(id="svg", label="SVG", components=["SVG"], in_beta=True),
    }
    return mapping[stack]


@router.get("/models", response_model=ModelsResponse)
async def get_models():
    # Keep legacy behavior of filtering out deprecated / older models.
    deprecated_models: Set[Llm] = {
        Llm.GPT_4_TURBO_2024_04_09,
        Llm.GPT_4_VISION,
        Llm.CLAUDE_3_SONNET,
        Llm.CLAUDE_3_OPUS,
        Llm.CLAUDE_3_HAIKU,
        Llm.GPT_4O_2024_05_13,
        Llm.GEMINI_2_0_FLASH_EXP,
        Llm.GEMINI_2_0_FLASH,
        Llm.GEMINI_2_0_PRO_EXP,
    }

    models: List[PublicModelInfo] = []
    for llm in Llm:
        if llm in deprecated_models:
            continue
        info = ModelRegistry.get(llm)
        models.append(
            PublicModelInfo(
                id=llm.value,
                name=_model_display_name(llm),
                provider=info.provider,
                supports_input_modes=sorted(info.supports_input_modes),
                supports_generation_types=sorted(info.supports_generation_types),
            )
        )

    available_stacks = list(Stack.__args__)
    stacks = [_stack_info(s) for s in available_stacks]

    # UI defaults / recommended models. Backend still enforces compatibility at runtime.
    defaults = {
        "generatedCodeConfig": "html_tailwind",
        "codeGenerationModel": Llm.GPT_5.value,
        "analysisModel": Llm.CLAUDE_4_5_OPUS_2025_11_01.value,
    }
    recommended = {
        "codeGenerationModels": [
            Llm.GPT_5.value,
            Llm.CLAUDE_4_5_SONNET_2025_11_01.value,
            Llm.GEMINI_3_PRO.value,
        ],
        "analysisModels": [
            Llm.CLAUDE_4_5_OPUS_2025_11_01.value,
            Llm.GPT_5.value,
            Llm.GEMINI_3_PRO.value,
        ],
    }

    return ModelsResponse(models=models, stacks=stacks, defaults=defaults, recommended=recommended)

