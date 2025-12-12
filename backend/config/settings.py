from __future__ import annotations

"""
Centralized backend configuration.

Uses pydantic-settings to load values from environment variables (and `.env`),
with correct boolean parsing. This is the authoritative source of config; the
`config` package re-exports legacy constant names for backward compatibility.
"""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Load from `.env` when present, but do not fail if missing.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # General
    NUM_VARIANTS: int = 1

    # LLM-related
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None

    # Image generation (optional)
    REPLICATE_API_KEY: Optional[str] = None

    # Debugging / feature flags
    MOCK: bool = False
    IS_DEBUG_ENABLED: bool = False
    DEBUG_DIR: str = ""

    # Production flag (feature gating)
    IS_PROD: bool = False

    # API hygiene / access control
    EVALS_API_KEY: Optional[str] = None

    # CORS
    CORS_ALLOW_ORIGINS: Optional[str] = None  # comma-separated

    # WebSocket hygiene
    WS_MAX_PAYLOAD_BYTES: int = 8_000_000


settings = Settings()
