"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Cognition API configuration
COGNITION_API_KEY = os.getenv("COGNITION_API_KEY")
COGNITION_API_BASE = os.getenv("COGNITION_API_BASE", "https://api.cognition.ai/v1")
COGNITION_API_URL = f"{COGNITION_API_BASE.rstrip('/')}/chat/completions"

# Council members - provider-prefixed model identifiers
COUNCIL_MODELS = [
    "openai/gpt-5.1",
    "google/gemini-3-pro-preview",
    "anthropic/claude-sonnet-4.5",
    "x-ai/grok-4",
    "cognition/swe-1.7",
]

# Chairman model - synthesizes final response
CHAIRMAN_MODEL = "google/gemini-3-pro-preview"

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Data directory for conversation storage
DATA_DIR = "data/conversations"
