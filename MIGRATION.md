# Migration Summary: Custom OpenAPI Client → Official OpenCode SDK

This document summarizes the migration from custom OpenAPI-generated client to the official OpenCode Python SDK.

## What Changed

### Before (Custom OpenAPI-Generated Client)
```python
# Manual client generation required
./generate_openapi_client.sh

# Import from generated package
from opencode_client import ApiClient, Configuration
from opencode_client.api.default_api import DefaultApi

# Configuration
OPENCODE_SERVER_URL = "http://127.0.0.1:4096"
OPENCODE_SERVER_USERNAME = "opencode"
OPENCODE_SERVER_PASSWORD = os.getenv("OPENCODE_SERVER_PASSWORD")
```

### After (Official OpenCode SDK)
```python
# Install from PyPI
pip install opencode-ai

# Import from official package
from opencode_ai import AsyncOpencode
from opencode_ai.types import TextPartInputParam

# Configuration
OPENCODE_SERVER_URL = "http://localhost:54321"  # SDK default port
```

## Key Benefits

1. **No Generation Required**
   - SDK is pre-built and maintained by OpenCode team
   - No Docker or openapi-generator needed
   - Simpler setup and deployment

2. **Official Support**
   - Actively maintained by the OpenCode team
   - Regular updates and bug fixes
   - Better documentation and examples

3. **Type Safety**
   - Pydantic models for all requests and responses
   - Full type hints for IDE autocomplete
   - Better error messages and validation

4. **Async Native**
   - Built-in async/await support via AsyncOpencode
   - No need for run_in_executor workarounds
   - Better performance for concurrent requests

## Migration Steps

For users migrating from the custom client to the official SDK:

### 1. Remove Generated Client
```bash
# Remove the generated client directory (if it exists)
rm -rf opencode_client/
```

### 2. Install Official SDK
```bash
# With pip
pip install opencode-ai

# Or with uv
uv sync  # Will install from pyproject.toml
```

### 3. Update Environment Variables
```bash
# Old .env (custom client)
OPENCODE_SERVER_URL=http://127.0.0.1:4096
OPENCODE_SERVER_USERNAME=opencode
OPENCODE_SERVER_PASSWORD=optional_password

# New .env (official SDK)
OPENCODE_SERVER_URL=http://localhost:54321  # SDK default port
# Authentication removed - SDK handles auth differently if needed
```

### 4. No Code Changes Required
The wrapper in `opencode_client_wrapper.py` has been updated to use the official SDK, but the external API remains the same. Your application code doesn't need changes.

## Architecture Changes

### Request Flow

**Before (Custom Client):**
```
App → opencode_client_wrapper.py → Generated Client → OpenCode Serve → LLM Providers
                                           ↓
                                   (requires generation)
```

**After (Official SDK):**
```
App → opencode_client_wrapper.py → Official SDK → OpenCode Serve → LLM Providers
                                         ↓
                                  (installed from PyPI)
```

### Client Management

**Before:**
- Generated client in `opencode_client/` directory (excluded from git)
- Requires Docker and openapi-generator
- Manual regeneration needed for updates
- Sync client wrapped with run_in_executor for async

**After:**
- SDK installed via pip: `pip install opencode-ai`
- No generation step required
- Updates via standard pip upgrade
- Native async support via AsyncOpencode

## Files Changed

### Removed/Deprecated
- `generate_openapi_client.sh` - No longer needed (now shows deprecation message)
- `opencode_client/` directory - No longer generated
- `openapi_spec.json` - No longer needed

### Modified Files
- `pyproject.toml` - Added `opencode-ai` dependency
- `backend/opencode_client_wrapper.py` - Updated to use official SDK
- `backend/config.py` - Removed auth configuration, updated default port
- `.env.example` - Updated environment variables
- `.gitignore` - Removed generated client references
- `README.md` - Updated setup instructions
- `CLAUDE.md` - Updated technical notes
- `TESTING.md` - Updated testing guide
- `MIGRATION.md` - Updated migration guide

### Unchanged Files
- `backend/council.py` - No changes needed (uses wrapper interface)
- `backend/storage.py` - No changes
- Frontend files - No changes

## Breaking Changes

### Configuration
- Model format unchanged: `"provider:model"` (e.g., `"openai:gpt-4"`)
- Default port changed: `4096` → `54321` (OpenCode SDK default)
- Authentication configuration removed (simpler setup)

### Environment
- No longer requires Docker for client generation
- No longer requires openapi-generator
- Simpler dependency installation

### Dependencies
- Removed: Custom generated `opencode_client` package
- Added: Official `opencode-ai` package from PyPI

## Compatibility

### What Stays the Same
- 3-stage council logic unchanged
- Frontend UI unchanged
- API endpoints unchanged
- Storage format unchanged
- Conversation history format unchanged

### What Changes
- Backend configuration
- Model identifiers format
- Authentication method
- API client implementation

## Rollback Plan

If needed, to rollback to the custom OpenAPI client:

1. Checkout the previous version from git
2. Run `./generate_openapi_client.sh` to generate the client
3. Update `.env` with old configuration
4. Install generated client: `cd opencode_client && pip install -e .`

Note: The official SDK is recommended for better maintainability and support.

## Performance Notes

### Latency
- **Custom Client**: ~1-3s per model query (depends on local OpenCode serve)
- **Official SDK**: Similar performance, with better async handling

### Concurrency
- Both support parallel queries via `asyncio.gather()`
- Official SDK has native async support (no run_in_executor overhead)
- Potentially better performance under high concurrency

### Resource Usage
- Official SDK: Lighter footprint (no generated code)
- Faster installation (no generation step)
- Smaller repository size

## Troubleshooting

### Common Issues

**"Failed to import opencode_ai"**
→ Run `pip install opencode-ai`

**"Connection refused to localhost:54321"**
→ Start `opencode serve` (uses port 54321 by default)

**"Model not available"**
→ Check `curl http://localhost:54321/config/providers`

**"Wrong port"**
→ Set `OPENCODE_SERVER_URL=http://localhost:54321` in `.env`

See TESTING.md for detailed troubleshooting.

## Future Improvements

1. **SDK Features**: Leverage new SDK features as they're released by OpenCode team
2. **Streaming**: Implement SSE for real-time responses when SDK supports it
3. **Error Recovery**: Better error handling with SDK's built-in retry logic
4. **Monitoring**: Use SDK's logging capabilities for better observability

## References

- [OpenCode Python SDK](https://github.com/anomalyco/opencode-sdk-python)
- [OpenCode Documentation](https://www.opencodecn.com/docs/server)
- [SDK on PyPI](https://pypi.org/project/opencode-ai/)
- [Testing Guide](TESTING.md)
- [Technical Notes](CLAUDE.md)

## Conclusion

The migration to the official OpenCode SDK simplifies setup, improves maintainability, and provides better long-term support. The official SDK is actively maintained by the OpenCode team and receives regular updates with new features and bug fixes.
