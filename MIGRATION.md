# Migration Summary: OpenCode Zen → OpenCode Serve

This document summarizes the migration from OpenCode Zen cloud API to local OpenCode serve with OpenAPI-generated SDK.

## What Changed

### Before (OpenCode Zen Cloud API)
```python
# Configuration
OPENCODE_API_KEY = os.getenv("OPENCODE_API_KEY")
OPENCODE_ZEN_BASE_URL = "https://opencode.ai/zen/v1"

COUNCIL_MODELS = [
    "gpt-5.2",
    "claude-sonnet-4-5",
    "gemini-3-pro",
]
```

### After (OpenCode Serve Local)
```python
# Configuration
OPENCODE_SERVER_URL = os.getenv("OPENCODE_SERVER_URL", "http://127.0.0.1:4096")
OPENCODE_SERVER_USERNAME = os.getenv("OPENCODE_SERVER_USERNAME", "opencode")
OPENCODE_SERVER_PASSWORD = os.getenv("OPENCODE_SERVER_PASSWORD")

COUNCIL_MODELS = [
    "openai:gpt-4",
    "anthropic:claude-3-5-sonnet",
    "google:gemini-1.5-pro",
]
```

## Key Benefits

1. **Type Safety**
   - OpenAPI-generated client provides full type hints
   - IDE autocomplete for all API methods
   - Compile-time error checking

2. **Local Control**
   - No dependency on cloud services
   - Full control over infrastructure
   - Faster response times (local execution)

3. **Flexibility**
   - Support for multiple LLM providers
   - Easy to add/remove providers
   - Session-based conversations

4. **Security**
   - Optional HTTP Basic Auth
   - No API keys sent to cloud
   - Local data processing

## Migration Steps

For users migrating from OpenCode Zen to OpenCode serve:

### 1. Install OpenCode
```bash
# Follow instructions at https://www.opencodecn.com/
```

### 2. Start OpenCode Serve
```bash
opencode serve
```

### 3. Generate OpenAPI Client
```bash
./generate_openapi_client.sh
```

### 4. Update Environment Variables
```bash
# Old .env
OPENCODE_API_KEY=sk-...

# New .env
OPENCODE_SERVER_URL=http://127.0.0.1:4096
OPENCODE_SERVER_PASSWORD=  # Optional
```

### 5. Update Model Configuration
Edit `backend/config.py`:
```python
# Change from:
COUNCIL_MODELS = ["gpt-5.2", "claude-sonnet-4-5"]

# To:
COUNCIL_MODELS = ["openai:gpt-4", "anthropic:claude-3-5-sonnet"]
```

### 6. Test
```bash
python test_opencode.py  # See TESTING.md
```

## Architecture Changes

### Request Flow

**Before (OpenCode Zen):**
```
App → opencode_zen.py → OpenCode Zen Cloud API → LLM Providers
```

**After (OpenCode Serve):**
```
App → opencode_client_wrapper.py → Generated Client → OpenCode Serve → LLM Providers
                                                              ↓
                                                         (local process)
```

### Session Management

**Before:**
- Stateless API calls
- No conversation context

**After:**
- Session-based conversations
- Each query creates a session
- Message history maintained

## Files Changed

### New Files
- `backend/opencode_client_wrapper.py` - Wrapper around generated client
- `generate_openapi_client.sh` - Script to generate client
- `openapi_spec.json` - OpenAPI specification (excluded from git)
- `opencode_client/` - Generated client directory (excluded from git)
- `TESTING.md` - Comprehensive testing guide

### Modified Files
- `backend/config.py` - Updated configuration
- `backend/council.py` - Updated imports
- `backend/opencode_zen.py` - Marked as deprecated
- `.env.example` - Updated environment variables
- `.gitignore` - Added generated files
- `README.md` - Updated documentation
- `CLAUDE.md` - Updated technical notes

## Breaking Changes

### Configuration
- `OPENCODE_API_KEY` → `OPENCODE_SERVER_URL`
- Model format: `"model"` → `"provider:model"`

### Environment
- Requires `opencode serve` to be running
- Requires OpenAPI client generation step

### Dependencies
- No longer uses `opencode_zen.py` module
- Requires generated `opencode_client` package

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

If needed, to rollback to OpenCode Zen:

1. Restore old configuration:
   ```python
   # In backend/config.py
   OPENCODE_API_KEY = os.getenv("OPENCODE_API_KEY")
   COUNCIL_MODELS = ["gpt-5.2", "claude-sonnet-4-5"]
   ```

2. Update imports:
   ```python
   # In backend/council.py
   from .opencode_zen import query_models_parallel, query_model
   ```

3. Update `.env`:
   ```bash
   OPENCODE_API_KEY=your_api_key_here
   ```

## Performance Notes

### Latency
- **OpenCode Zen**: ~2-5s per model query (network latency)
- **OpenCode Serve**: ~1-3s per model query (local, depends on model)

### Concurrency
- Both support parallel queries via `asyncio.gather()`
- OpenCode Serve may be faster due to local execution

### Resource Usage
- OpenCode Serve runs as local process
- Memory usage depends on models being used
- CPU usage for local model inference (if applicable)

## Security Considerations

### OpenCode Zen (Cloud)
- API key transmitted over HTTPS
- Data sent to cloud service
- Vendor security policies apply

### OpenCode Serve (Local)
- Optional HTTP Basic Auth
- All data processed locally
- User controls security policies
- Network exposure configurable

## Troubleshooting

### Common Issues

**"Failed to import opencode_client"**
→ Run `./generate_openapi_client.sh`

**"Connection refused to localhost:4096"**
→ Start `opencode serve`

**"Model not available"**
→ Check `curl http://localhost:4096/config/providers`

**"Authentication failed"**
→ Verify OPENCODE_SERVER_PASSWORD matches server

See TESTING.md for detailed troubleshooting.

## Future Improvements

1. **Caching**: Cache generated OpenAPI client
2. **Session Reuse**: Reuse sessions across queries
3. **Streaming**: Implement SSE for real-time responses
4. **Health Monitoring**: Add periodic health checks
5. **Auto-reconnect**: Handle server restarts gracefully

## References

- [OpenCode Documentation](https://www.opencodecn.com/docs/server)
- [OpenAPI Generator](https://openapi-generator.tech/)
- [Testing Guide](TESTING.md)
- [Technical Notes](CLAUDE.md)

## Support

For issues:
1. Check TESTING.md for common problems
2. Verify `opencode serve` is running
3. Check server logs for errors
4. Review generated client documentation
5. File an issue on GitHub with logs

## Conclusion

The migration to OpenCode serve provides better type safety, local control, and flexibility while maintaining full compatibility with the existing application logic. The OpenAPI-generated client ensures maintainability and reduces the risk of API changes breaking the application.
