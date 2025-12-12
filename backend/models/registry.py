from __future__ import annotations

"""
Model registry and capabilities.

This module centralizes:
  - provider ownership
  - which input modes / generation types are supported
  - provider-specific generation parameters (streaming, token limits, etc.)

Streaming clients read their model-specific parameters from here.
"""

from dataclasses import dataclass
from typing import Dict, Literal, Optional, Sequence, Set

from custom_types import InputMode
from llm import Llm, MODEL_PROVIDER

Provider = Literal["openai", "anthropic", "gemini"]
GenerationType = Literal["create", "update"]


@dataclass(frozen=True)
class OpenAIParams:
    supports_streaming: bool = True
    supports_temperature: bool = True
    temperature: Optional[float] = 0.0
    max_tokens: Optional[int] = None
    max_completion_tokens: Optional[int] = None
    reasoning_effort: Optional[Literal["low", "medium", "high"]] = None


@dataclass(frozen=True)
class AnthropicParams:
    max_tokens: int = 8192
    temperature: float = 0.0
    use_thinking: bool = False
    thinking_budget_tokens: Optional[int] = None
    betas: Sequence[str] = ("output-128k-2025-02-19",)


@dataclass(frozen=True)
class GeminiParams:
    max_output_tokens: int = 8000
    temperature: float = 0.0
    thinking_budget: Optional[int] = None
    include_thoughts: bool = False


@dataclass(frozen=True)
class ModelInfo:
    llm: Llm
    provider: Provider
    supports_input_modes: Set[InputMode]
    supports_generation_types: Set[GenerationType]
    openai: Optional[OpenAIParams] = None
    anthropic: Optional[AnthropicParams] = None
    gemini: Optional[GeminiParams] = None


class ModelRegistry:
    _DEFAULT_OPENAI = OpenAIParams()
    _DEFAULT_ANTHROPIC = AnthropicParams()
    _DEFAULT_GEMINI = GeminiParams()

    # Latest models per provider used for fallback selection.
    LATEST_BY_PROVIDER: Dict[Provider, Llm] = {
        "openai": Llm.GPT_5,
        "anthropic": Llm.CLAUDE_4_5_OPUS_2025_11_01,
        "gemini": Llm.GEMINI_3_PRO,
    }

    _MODELS: Dict[Llm, ModelInfo] = {}

    # Build defaults by provider.
    for llm, provider_str in MODEL_PROVIDER.items():
        provider = provider_str  # type: ignore
        if provider == "openai":
            _MODELS[llm] = ModelInfo(
                llm=llm,
                provider="openai",
                supports_input_modes={"text", "image"},
                supports_generation_types={"create", "update"},
                openai=_DEFAULT_OPENAI,
            )
        elif provider == "anthropic":
            _MODELS[llm] = ModelInfo(
                llm=llm,
                provider="anthropic",
                supports_input_modes={"text", "image", "video"},
                supports_generation_types={"create", "update"},
                anthropic=_DEFAULT_ANTHROPIC,
            )
        elif provider == "gemini":
            _MODELS[llm] = ModelInfo(
                llm=llm,
                provider="gemini",
                supports_input_modes={"image"},
                supports_generation_types={"create"},
                gemini=_DEFAULT_GEMINI,
            )

    # OpenAI overrides
    _MODELS[Llm.GPT_5] = _MODELS[Llm.GPT_5].__class__(  # type: ignore
        **{
            **_MODELS[Llm.GPT_5].__dict__,
            "openai": OpenAIParams(
                supports_streaming=True,
                supports_temperature=True,
                temperature=1.0,
                max_completion_tokens=32768,
            ),
        }
    )
    _MODELS[Llm.GPT_5_TURBO] = _MODELS[Llm.GPT_5_TURBO].__class__(  # type: ignore
        **{
            **_MODELS[Llm.GPT_5_TURBO].__dict__,
            "openai": OpenAIParams(
                supports_streaming=True,
                supports_temperature=True,
                temperature=1.0,
                max_completion_tokens=32768,
            ),
        }
    )
    for llm in (
        Llm.GPT_4_1_2025_04_14,
        Llm.GPT_4_1_MINI_2025_04_14,
        Llm.GPT_4_1_NANO_2025_04_14,
    ):
        _MODELS[llm] = _MODELS[llm].__class__(  # type: ignore
            **{
                **_MODELS[llm].__dict__,
                "openai": OpenAIParams(
                    supports_streaming=True,
                    supports_temperature=True,
                    temperature=0.0,
                    max_tokens=20000,
                ),
            }
        )

    _MODELS[Llm.GPT_4O_2024_05_13] = _MODELS[Llm.GPT_4O_2024_05_13].__class__(  # type: ignore
        **{
            **_MODELS[Llm.GPT_4O_2024_05_13].__dict__,
            "openai": OpenAIParams(max_tokens=4096),
        }
    )
    _MODELS[Llm.GPT_4O_2024_11_20] = _MODELS[Llm.GPT_4O_2024_11_20].__class__(  # type: ignore
        **{
            **_MODELS[Llm.GPT_4O_2024_11_20].__dict__,
            "openai": OpenAIParams(max_tokens=16384),
        }
    )
    _MODELS[Llm.O1_2024_12_17] = _MODELS[Llm.O1_2024_12_17].__class__(  # type: ignore
        **{
            **_MODELS[Llm.O1_2024_12_17].__dict__,
            "openai": OpenAIParams(
                supports_streaming=False,
                supports_temperature=False,
                temperature=None,
                max_completion_tokens=20000,
            ),
        }
    )
    for llm in (Llm.O4_MINI_2025_04_16, Llm.O3_2025_04_16):
        _MODELS[llm] = _MODELS[llm].__class__(  # type: ignore
            **{
                **_MODELS[llm].__dict__,
                "openai": OpenAIParams(
                    supports_streaming=True,
                    supports_temperature=False,
                    temperature=None,
                    max_completion_tokens=20000,
                    reasoning_effort="high",
                ),
            }
        )

    # Anthropic overrides
    _MODELS[Llm.CLAUDE_3_7_SONNET_2025_02_19] = _MODELS[
        Llm.CLAUDE_3_7_SONNET_2025_02_19
    ].__class__(  # type: ignore
        **{
            **_MODELS[Llm.CLAUDE_3_7_SONNET_2025_02_19].__dict__,
            "anthropic": AnthropicParams(max_tokens=20000),
        }
    )
    for llm in (Llm.CLAUDE_4_SONNET_2025_05_14, Llm.CLAUDE_4_OPUS_2025_05_14):
        _MODELS[llm] = _MODELS[llm].__class__(  # type: ignore
            **{
                **_MODELS[llm].__dict__,
                "anthropic": AnthropicParams(
                    max_tokens=30000,
                    temperature=0.0,
                    use_thinking=True,
                    thinking_budget_tokens=10000,
                    betas=(),
                ),
            }
        )

    # Gemini overrides
    _MODELS[Llm.GEMINI_2_5_FLASH_PREVIEW_05_20] = _MODELS[
        Llm.GEMINI_2_5_FLASH_PREVIEW_05_20
    ].__class__(  # type: ignore
        **{
            **_MODELS[Llm.GEMINI_2_5_FLASH_PREVIEW_05_20].__dict__,
            "gemini": GeminiParams(
                temperature=0.0,
                max_output_tokens=20000,
                thinking_budget=5000,
                include_thoughts=True,
            ),
        }
    )
    _MODELS[Llm.GEMINI_3_PRO] = _MODELS[Llm.GEMINI_3_PRO].__class__(  # type: ignore
        **{
            **_MODELS[Llm.GEMINI_3_PRO].__dict__,
            "gemini": GeminiParams(temperature=0.0, max_output_tokens=32768),
        }
    )

    @classmethod
    def from_name(cls, model_name: str) -> Llm:
        for llm in Llm:
            if llm.value == model_name:
                return llm
        raise ValueError(f"Unknown model name: {model_name}")

    @classmethod
    def get(cls, llm: Llm) -> ModelInfo:
        return cls._MODELS[llm]

    @classmethod
    def provider(cls, llm: Llm) -> Provider:
        return cls.get(llm).provider

    @classmethod
    def latest_for_provider(cls, provider: Provider) -> Llm:
        return cls.LATEST_BY_PROVIDER[provider]

    @classmethod
    def is_compatible(
        cls, llm: Llm, generation_type: GenerationType, input_mode: InputMode
    ) -> bool:
        info = cls.get(llm)
        return (
            generation_type in info.supports_generation_types
            and input_mode in info.supports_input_modes
        )

    @classmethod
    def openai_params(cls, llm: Llm) -> OpenAIParams:
        info = cls.get(llm)
        if info.openai is None:
            raise ValueError(f"{llm.value} is not an OpenAI model")
        return info.openai

    @classmethod
    def anthropic_params(cls, llm: Llm) -> AnthropicParams:
        info = cls.get(llm)
        if info.anthropic is None:
            raise ValueError(f"{llm.value} is not an Anthropic model")
        return info.anthropic

    @classmethod
    def gemini_params(cls, llm: Llm) -> GeminiParams:
        info = cls.get(llm)
        if info.gemini is None:
            raise ValueError(f"{llm.value} is not a Gemini model")
        return info.gemini

