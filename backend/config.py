"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenCode serve configuration
# Server URL (defaults to local server on port 54321, which is the official OpenCode SDK default port)
OPENCODE_SERVER_URL = os.getenv("OPENCODE_SERVER_URL", "http://localhost:54321")

# Council members - list of model identifiers in format "provider:model"
# Examples: "openai:gpt-4", "anthropic:claude-3-5-sonnet", "google:gemini-1.5-pro"
# MINIMUM REQUIREMENT: At least 2 models are required for meaningful peer review
COUNCIL_MODELS = [
    "openai:gpt-4",
    "anthropic:claude-3-5-sonnet",
    "google:gemini-1.5-pro",
    "openai:gpt-4-turbo",
]

# Chairman model - synthesizes final response
# Can be the same as one of the council models or a different model
CHAIRMAN_MODEL = "openai:gpt-4"

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
    if not OPENCODE_SERVER_URL:
        return False, "OPENCODE_SERVER_URL is not set. Please configure the server URL in .env file."
    
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
