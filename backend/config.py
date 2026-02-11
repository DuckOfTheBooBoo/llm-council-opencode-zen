"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenCode Zen API key
OPENCODE_API_KEY = os.getenv("OPENCODE_API_KEY")

# OpenCode Zen API base URL
OPENCODE_ZEN_BASE_URL = "https://opencode.ai/zen/v1"

# Council members - list of OpenCode Zen model identifiers
# MINIMUM REQUIREMENT: At least 2 models are required for meaningful peer review
COUNCIL_MODELS = [
    "gpt-5.2",
    "claude-sonnet-4-5",
    "gemini-3-pro",
    "qwen3-coder",
    "gpt-5.1-codex",
]

# Chairman model - synthesizes final response
# Can be the same as one of the council models or a different model
CHAIRMAN_MODEL = "gpt-5.2"

# Data directory for conversation storage
DATA_DIR = "data/conversations"

# Minimum number of council models required
MIN_COUNCIL_MODELS = 2


def validate_config() -> tuple[bool, str]:
    """
    Validate the LLM Council configuration.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not OPENCODE_API_KEY:
        return False, "OPENCODE_API_KEY is not set. Please configure your API key in .env file."
    
    if not COUNCIL_MODELS:
        return False, "COUNCIL_MODELS is empty. At least 2 council models are required."
    
    if len(COUNCIL_MODELS) < MIN_COUNCIL_MODELS:
        return False, f"At least {MIN_COUNCIL_MODELS} council models are required for meaningful peer review, but only {len(COUNCIL_MODELS)} configured."
    
    if not CHAIRMAN_MODEL:
        return False, "CHAIRMAN_MODEL is not set. A chairman model is required to synthesize the final response."
    
    return True, ""


def get_config_info() -> dict:
    """
    Get information about the current configuration.
    
    Returns:
        Dictionary with configuration details
    """
    return {
        "council_models": COUNCIL_MODELS,
        "council_models_count": len(COUNCIL_MODELS),
        "chairman_model": CHAIRMAN_MODEL,
        "min_required_models": MIN_COUNCIL_MODELS,
        "is_valid": validate_config()[0]
    }
