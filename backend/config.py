"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenCode Zen API key
OPENCODE_API_KEY = os.getenv("OPENCODE_API_KEY")

# OpenCode Zen API base URL
OPENCODE_ZEN_BASE_URL = "https://opencode.ai/zen/v1"

# Council members - list of OpenCode Zen model identifiers
COUNCIL_MODELS = [
    "gpt-5.2",
    "claude-sonnet-4-5",
    "gemini-3-pro",
    "qwen3-coder",
    "gpt-5.1-codex",
]

# Chairman model - synthesizes final response
CHAIRMAN_MODEL = "gpt-5.2"

# Data directory for conversation storage
DATA_DIR = "data/conversations"
