"""Wrapper around OpenCode serve generated client for LLM requests."""

import asyncio
from typing import List, Dict, Any, Optional
import sys
import os

# Add the generated client to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'opencode_client'))

try:
    from opencode_client import ApiClient, Configuration
    from opencode_client.api.default_api import DefaultApi
    from opencode_client.models.create_session_request import CreateSessionRequest
    from opencode_client.models.send_message_request import SendMessageRequest
    from opencode_client.models.part import Part
except ImportError as e:
    print(f"Error importing generated OpenCode client: {e}")
    print("Please run ./generate_openapi_client.sh to generate the client")
    raise

from .config import (
    OPENCODE_SERVER_URL,
    OPENCODE_SERVER_USERNAME,
    OPENCODE_SERVER_PASSWORD
)


def get_api_client() -> DefaultApi:
    """
    Get configured API client with authentication.
    
    Returns:
        Configured DefaultApi instance
    """
    configuration = Configuration(
        host=OPENCODE_SERVER_URL
    )
    
    # Set up HTTP Basic Auth if password is configured
    if OPENCODE_SERVER_PASSWORD:
        configuration.username = OPENCODE_SERVER_USERNAME
        configuration.password = OPENCODE_SERVER_PASSWORD
    
    api_client = ApiClient(configuration)
    return DefaultApi(api_client)


async def check_health() -> bool:
    """
    Check if OpenCode serve is running and healthy.
    
    Returns:
        True if server is healthy, False otherwise
    """
    try:
        api = get_api_client()
        # Run sync API in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, api.get_health)
        return response.healthy if hasattr(response, 'healthy') else False
    except Exception as e:
        print(f"Health check failed: {e}")
        return False


async def create_session(title: Optional[str] = None, parent_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Create a new session.
    
    Args:
        title: Optional session title
        parent_id: Optional parent session ID
        
    Returns:
        Session object with 'id' field, or None if failed
    """
    try:
        api = get_api_client()
        request_data = {}
        if title:
            request_data['title'] = title
        if parent_id:
            request_data['parent_id'] = parent_id
        
        # Run sync API in thread pool
        loop = asyncio.get_event_loop()
        session = await loop.run_in_executor(
            None, 
            api.create_session,
            CreateSessionRequest(**request_data) if request_data else None
        )
        
        # Convert to dict
        if hasattr(session, 'to_dict'):
            return session.to_dict()
        return {'id': session.id} if hasattr(session, 'id') else None
        
    except Exception as e:
        print(f"Failed to create session: {e}")
        return None


async def send_message(
    session_id: str,
    text: str,
    model: Optional[str] = None,
    system: Optional[str] = None,
    timeout: float = 600.0
) -> Optional[Dict[str, Any]]:
    """
    Send a message to a session and wait for response.
    
    Args:
        session_id: Session ID
        text: Message text
        model: Optional model identifier (e.g., "openai:gpt-4")
        system: Optional system prompt
        timeout: Request timeout in seconds (not used with generated client)
        
    Returns:
        Response dict with 'info' and 'parts', or None if failed
    """
    try:
        api = get_api_client()
        
        # Create message parts
        part = Part(type="text", text=text)
        
        # Build request
        request_data = {
            'parts': [part],
            'no_reply': False
        }
        
        if model:
            request_data['model'] = model
        if system:
            request_data['system'] = system
        
        message_request = SendMessageRequest(**request_data)
        
        # Run sync API in thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            api.send_message,
            session_id,
            message_request
        )
        
        # Convert to dict
        if hasattr(response, 'to_dict'):
            return response.to_dict()
        
        # Extract parts manually
        result = {
            'info': response.info.to_dict() if hasattr(response, 'info') and hasattr(response.info, 'to_dict') else {},
            'parts': [p.to_dict() if hasattr(p, 'to_dict') else p for p in (response.parts if hasattr(response, 'parts') else [])]
        }
        return result
        
    except Exception as e:
        print(f"Failed to send message: {e}")
        return None


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """
    Query a single model via OpenCode serve.
    
    Creates a temporary session, sends messages, and extracts the response.
    
    Args:
        model: Model identifier (e.g., "openai:gpt-4", "anthropic:claude-3-5-sonnet")
        messages: List of message dicts with 'role' and 'content'
        timeout: Request timeout in seconds
        
    Returns:
        Response dict with 'content' and optional 'reasoning_details', or None if failed
    """
    try:
        # Create a session for this query
        session = await create_session(title=f"Council query: {model}")
        if not session or 'id' not in session:
            print(f"Failed to create session for model {model}")
            return None
            
        session_id = session["id"]
        
        # Build the conversation text from messages
        # System messages go to system param, user/assistant messages to text
        system_messages = [m["content"] for m in messages if m.get("role") == "system"]
        conversation_messages = [m for m in messages if m.get("role") != "system"]
        
        # Format conversation
        conversation_text = ""
        for msg in conversation_messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                conversation_text += f"{content}\n"
            elif role == "assistant":
                conversation_text += f"Assistant: {content}\n"
        
        # Send the message
        system_prompt = "\n".join(system_messages) if system_messages else None
        response = await send_message(
            session_id=session_id,
            text=conversation_text.strip(),
            model=model,
            system=system_prompt,
            timeout=timeout
        )
        
        if not response:
            print(f"No response from model {model}")
            return None
            
        # Extract content from parts
        parts = response.get("parts", [])
        content_parts = []
        for part in parts:
            if isinstance(part, dict):
                if part.get("type") == "text":
                    content_parts.append(part.get("text", ""))
            elif hasattr(part, 'type') and part.type == "text":
                content_parts.append(part.text if hasattr(part, 'text') else "")
        
        content = "\n".join(content_parts)
        
        return {
            "content": content,
            "reasoning_details": None  # OpenCode serve doesn't provide this in the same format
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
        models: List of model identifiers
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
