# Testing Guide for OpenCode Serve Migration

This document provides instructions for manually testing the OpenCode serve integration.

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
# Start on default port (127.0.0.1:4096)
opencode serve
```

**Expected output:**
```
OpenCode Server starting...
OpenCode Server listening on http://127.0.0.1:4096
Documentation available at http://127.0.0.1:4096/doc
```

Verify the server is running before proceeding to the next step.

### With Authentication (Optional)
```bash
# Enable HTTP Basic Auth
export OPENCODE_SERVER_PASSWORD=your_secure_password
export OPENCODE_SERVER_USERNAME=opencode  # Optional, defaults to "opencode"
opencode serve
```

### For Network Access (Optional)
```bash
# Allow access from other machines/containers
opencode serve --hostname 0.0.0.0 --port 4096
```

The server should start and display:
```
OpenCode Server listening on http://127.0.0.1:4096
```

## Step 2: Verify Server Health

```bash
# Check health endpoint
curl http://localhost:4096/global/health

# Expected output:
# {"healthy": true, "version": "..."}
```

## Step 3: Check Available Providers

```bash
# List available providers and models
curl http://localhost:4096/config/providers

# This shows what providers are configured and their default models
```

## Step 4: Generate OpenAPI Client

```bash
# From the project root
./generate_openapi_client.sh
```

This script will:
1. Fetch the OpenAPI spec from the running server
2. Generate a Python client using Docker and openapi-generator
3. Place the generated client in `opencode_client/` directory

**Troubleshooting:**
- If the script fails to extract the spec from HTML, manually visit http://localhost:4096/doc
- Save the OpenAPI JSON spec to `openapi_spec.json`
- Re-run the generation script

## Step 5: Configure Environment

Create/update `.env` file:

```bash
# OpenCode serve URL
OPENCODE_SERVER_URL=http://127.0.0.1:4096

# Optional: HTTP Basic Auth (if you set OPENCODE_SERVER_PASSWORD when starting serve)
OPENCODE_SERVER_USERNAME=opencode
OPENCODE_SERVER_PASSWORD=your_secure_password
```

## Step 6: Configure Models

Edit `backend/config.py` to match your available providers:

```python
# Use provider:model format
# Check available models at http://localhost:4096/config/providers
COUNCIL_MODELS = [
    "openai:gpt-4",
    "anthropic:claude-3-5-sonnet",
    "google:gemini-1.5-pro",
    "openai:gpt-4-turbo",
]

CHAIRMAN_MODEL = "openai:gpt-4"
```

**Important:** Only use models that are available in your OpenCode serve instance.

## Step 7: Install Python Dependencies

```bash
# Install project dependencies
uv sync

# Install the generated OpenAPI client
cd opencode_client
pip install -e .
cd ..
```

## Step 8: Test Backend Connectivity

Create a test script `test_opencode.py`:

```python
import asyncio
from backend.opencode_client_wrapper import check_health, query_model

async def test():
    # Test health check
    print("Testing health check...")
    healthy = await check_health()
    print(f"Server healthy: {healthy}")
    
    if not healthy:
        print("Server is not healthy. Make sure 'opencode serve' is running.")
        return
    
    # Test single model query
    print("\nTesting model query...")
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
Testing health check...
Server healthy: True

Testing model query...
Model response: Hello back!
```

## Step 9: Start the Application

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

## Step 10: Test Full Council Flow

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
2. Check OPENCODE_SERVER_URL in `.env`
3. Test health endpoint: `curl http://localhost:4096/global/health`

### Issue: "Error importing generated OpenCode client"
**Cause:** OpenAPI client not generated
**Solution:**
1. Run `./generate_openapi_client.sh`
2. Install the client: `cd opencode_client && pip install -e . && cd ..`

### Issue: "Model [provider:model] not available"
**Cause:** Model not configured in OpenCode serve
**Solution:**
1. Check available models: `curl http://localhost:4096/config/providers`
2. Update `backend/config.py` with available models
3. Ensure provider API keys are configured in OpenCode

### Issue: Authentication errors (401 Unauthorized)
**Cause:** Mismatched authentication configuration
**Solution:**
1. If using auth, ensure OPENCODE_SERVER_PASSWORD matches server password
2. If not using auth, leave OPENCODE_SERVER_PASSWORD empty in `.env`

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

# Optional: Clean generated client to regenerate fresh
rm -rf opencode_client/
```

## Next Steps

After successful testing:
1. Document any issues encountered
2. Update configuration as needed
3. Consider removing or archiving old `opencode_zen.py` file
4. Run security checks
5. Deploy to production environment if applicable
