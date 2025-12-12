"""
Backward-compatible config exports.

All configuration is loaded in `config.settings.Settings` using pydantic-settings.
This module re-exports the historical constant names so existing imports keep
working.
"""

from .settings import settings

# General
NUM_VARIANTS = settings.NUM_VARIANTS

# LLM-related
OPENAI_API_KEY = settings.OPENAI_API_KEY
ANTHROPIC_API_KEY = settings.ANTHROPIC_API_KEY
GEMINI_API_KEY = settings.GEMINI_API_KEY
OPENAI_BASE_URL = settings.OPENAI_BASE_URL

# Image generation (optional)
REPLICATE_API_KEY = settings.REPLICATE_API_KEY

# Debugging-related / feature flags
SHOULD_MOCK_AI_RESPONSE = settings.MOCK
IS_DEBUG_ENABLED = settings.IS_DEBUG_ENABLED
DEBUG_DIR = settings.DEBUG_DIR

# Production flag
IS_PROD = settings.IS_PROD

# API hygiene / access control
EVALS_API_KEY = settings.EVALS_API_KEY

# CORS
CORS_ALLOW_ORIGINS = settings.CORS_ALLOW_ORIGINS

# WebSocket hygiene
WS_MAX_PAYLOAD_BYTES = settings.WS_MAX_PAYLOAD_BYTES
