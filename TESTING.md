# Testing Guide for OpenCode SDK Integration

This document provides instructions for manually testing the OpenCode SDK integration.

## Prerequisites

1. **Install OpenCode** (if not already installed)
   - Follow instructions at https://www.opencodecn.com/
   - Verify installation: `opencode --version`

2. **Configure LLM Provider API Keys**
   - OpenCode serve needs API keys for providers (OpenAI, Anthropic, etc.)
   - Set up your provider keys according to OpenCode documentation

## Step 1: Start OpenCode Serve

### Local Testing (Default)
```bash
# Start on default port (localhost:54321)
opencode serve
```

**Expected output:**
```
OpenCode Server starting...
OpenCode Server listening on http://localhost:54321
Documentation available at http://localhost:54321/doc
```

Verify the server is running before proceeding to the next step.

## Step 2: Install Dependencies

```bash
# Install project dependencies with uv
uv sync

# Or with pip (from project root)
pip install -e .
```

The official OpenCode SDK (`opencode-ai`) will be installed automatically.

## Step 3: Configure Environment

Create/update `.env` file:

```bash
# OpenCode serve URL (defaults to http://localhost:54321 if not set)
OPENCODE_SERVER_URL=http://localhost:54321
```

## Step 4: Configure Models

Edit `backend/config.py` to match your available providers:

```python
# Use provider:model format
# Check available models at http://localhost:54321/config/providers
COUNCIL_MODELS = [
    "openai:gpt-4",
    "anthropic:claude-3-5-sonnet",
    "google:gemini-1.5-pro",
    "openai:gpt-4-turbo",
]

CHAIRMAN_MODEL = "openai:gpt-4"
```

**Important:** Only use models that are available in your OpenCode serve instance.

## Step 5: Test Backend Connectivity

Create a test script `test_opencode.py`:

```python
import asyncio
from backend.opencode_client_wrapper import query_model

async def test():
    # Test with a simple query
    print("Testing OpenCode SDK integration...")
    messages = [{"role": "user", "content": "Hello! Please respond with 'Hello back!'"}]
    response = await query_model("openai:gpt-4", messages)
    
    if response:
        print(f"Model response: {response['content']}")
    else:
        print("Failed to get response from model")

if __name__ == "__main__":
    asyncio.run(test())
```

Run the test:
```bash
python test_opencode.py
```

**Expected output:**
```
Testing OpenCode SDK integration...
Model response: Hello back!
```

## Step 6: Start the Application

### Terminal 1: Backend
```bash
uv run python -m backend.main
```

**Expected output:**
```
✓ Configuration validated successfully
✓ Council models: 4
✓ Chairman model: openai:gpt-4
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

**Expected output:**
```
VITE ready in XXX ms
➜  Local:   http://localhost:5173/
```

## Step 7: Test Full Council Flow

1. Open http://localhost:5173 in your browser
2. Click "New Conversation"
3. Type a test query, e.g., "What is the capital of France?"
4. Submit and wait for responses

**Verify:**
- ✅ Stage 1 shows individual responses from all council models
- ✅ Stage 2 shows peer reviews and rankings
- ✅ Stage 3 shows final synthesized answer
- ✅ Configuration panel at bottom shows correct models

## Common Issues

### Issue: "Failed to create session"
**Cause:** OpenCode serve is not running or URL is incorrect
**Solution:**
1. Verify `opencode serve` is running
2. Check OPENCODE_SERVER_URL in `.env` (default: http://localhost:54321)
3. Test server: `curl http://localhost:54321/config/providers`

### Issue: "Error importing OpenCode SDK"
**Cause:** SDK not installed
**Solution:**
1. Run `pip install opencode-ai`
2. Or run `uv sync` to install all dependencies

### Issue: "Model [provider:model] not available"
**Cause:** Model not configured in OpenCode serve
**Solution:**
1. Check available models: `curl http://localhost:54321/config/providers`
2. Update `backend/config.py` with available models
3. Ensure provider API keys are configured in OpenCode

### Issue: "No response from model"
**Cause:** Model query timeout or failure
**Solution:**
1. Check OpenCode serve logs for errors
2. Verify provider API keys are valid
3. Try with a different model
4. Increase timeout in wrapper if needed

## Performance Testing

Test with different numbers of council models:

```python
# In backend/config.py
COUNCIL_MODELS = [
    "openai:gpt-4",
    "anthropic:claude-3-5-sonnet",
]  # Minimum: 2 models

# vs

COUNCIL_MODELS = [
    "openai:gpt-4",
    "openai:gpt-4-turbo",
    "anthropic:claude-3-5-sonnet",
    "anthropic:claude-3-opus",
    "google:gemini-1.5-pro",
]  # More models = more diverse but slower
```

**Expected behavior:**
- Queries should complete successfully with 2+ models
- Response time increases with more models (parallel execution helps)
- All stages should complete even if some models fail (graceful degradation)

## Cleanup After Testing

```bash
# Stop OpenCode serve (Ctrl+C in the terminal where it's running)

# Stop backend (Ctrl+C)

# Stop frontend (Ctrl+C)
```

## Next Steps

After successful testing:
1. Document any issues encountered
2. Update configuration as needed
3. Run security checks with code review tools
4. Deploy to production environment if applicable
