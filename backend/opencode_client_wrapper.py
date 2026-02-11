"""Wrapper around official OpenCode SDK for LLM requests."""

import asyncio
from typing import List, Dict, Any, Optional

try:
    from opencode_ai import AsyncOpencode
    from opencode_ai.types import TextPartInputParam
except ImportError as e:
    print(f"Error importing OpenCode SDK: {e}")
    print("Please install the SDK: pip install opencode-ai")
    raise

from .config import OPENCODE_SERVER_URL


def get_api_client() -> AsyncOpencode:
    """
    Get configured async API client.
    
    Returns:
        Configured AsyncOpencode instance
    """
    return AsyncOpencode(
        base_url=OPENCODE_SERVER_URL,
        timeout=120.0,
    )


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """
    Query a single model via OpenCode SDK.
    
    Creates a temporary session, sends messages, and extracts the response.
    
    Args:
        model: Model identifier in "provider:model" format (e.g., "openai:gpt-4")
        messages: List of message dicts with 'role' and 'content'
        timeout: Request timeout in seconds
        
    Returns:
        Response dict with 'content' and optional 'reasoning_details', or None if failed
    """
    try:
        # Parse provider and model from format "provider:model"
        if ":" not in model:
            print(f"Invalid model format '{model}'. Expected \"provider:model\" format (e.g., \"openai:gpt-4\")")
            return None
            
        provider_id, model_id = model.split(":", 1)
        
        # Create client
        client = get_api_client()
        
        # Create a session for this query
        session = await client.session.create()
        session_id = session.id
        
        # Build the conversation text from messages
        # System messages go to system param, user/assistant messages to parts
        system_messages = [m["content"] for m in messages if m.get("role") == "system"]
        conversation_messages = [m for m in messages if m.get("role") != "system"]
        
        # Format conversation text
        conversation_text = ""
        for msg in conversation_messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                conversation_text += f"{content}\n"
            elif role == "assistant":
                conversation_text += f"Assistant: {content}\n"
        
        # Create text part
        text_part = TextPartInputParam(text=conversation_text.strip())
        
        # Send the message
        system_prompt = "\n".join(system_messages) if system_messages else None
        
        response = await client.session.chat(
            id=session_id,
            provider_id=provider_id,
            model_id=model_id,
            parts=[text_part],
            system=system_prompt if system_prompt else None,
            timeout=timeout
        )
        
        # Extract content from response parts
        content_parts = []
        for part in response.parts:
            if hasattr(part, 'text') and part.text:
                content_parts.append(part.text)
        
        content = "\n".join(content_parts)
        
        return {
            "content": content,
            # The reasoning_details field maintains API compatibility
            "reasoning_details": None
        }
        
    except Exception as e:
        print(f"Error querying model {model}: {e}")
        import traceback
        traceback.print_exc()
        return None


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multiple models in parallel.
    
    Args:
        models: List of model identifiers in "provider:model" format
        messages: List of message dicts to send to each model
        
    Returns:
        Dict mapping model identifier to response dict (or None if failed)
    """
    # Create tasks for all models
    tasks = [query_model(model, messages) for model in models]
    
    # Wait for all to complete
    responses = await asyncio.gather(*tasks)
    
    # Map models to their responses
    return {model: response for model, response in zip(models, responses)}
