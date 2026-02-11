# LLM Council

![llmcouncil](header.jpg)

The idea of this repo is that instead of asking a question to your favorite LLM provider (e.g. OpenAI GPT-4, Google Gemini, Anthropic Claude, etc.), you can group them into your "LLM Council". This repo is a simple, local web app that essentially looks like ChatGPT except it uses OpenCode serve to send your query to multiple LLMs, it then asks them to review and rank each other's work, and finally a Chairman LLM produces the final response.

In a bit more detail, here is what happens when you submit a query:

1. **Stage 1: First opinions**. The user query is given to all LLMs individually, and the responses are collected. The individual responses are shown in a "tab view", so that the user can inspect them all one by one.
2. **Stage 2: Review**. Each individual LLM is given the responses of the other LLMs. Under the hood, the LLM identities are anonymized so that the LLM can't play favorites when judging their outputs. The LLM is asked to rank them in accuracy and insight.
3. **Stage 3: Final response**. The designated Chairman of the LLM Council takes all of the model's responses and compiles them into a single final answer that is presented to the user.

## Vibe Code Alert

This project was 99% vibe coded as a fun Saturday hack because I wanted to explore and evaluate a number of LLMs side by side in the process of [reading books together with LLMs](https://x.com/karpathy/status/1990577951671509438). It's nice and useful to see multiple responses side by side, and also the cross-opinions of all LLMs on each other's outputs. I'm not going to support it in any way, it's provided here as is for other people's inspiration and I don't intend to improve it. Code is ephemeral now and libraries are over, ask your LLM to change it in whatever way you like.

## Setup

### 1. Start OpenCode Serve

This application uses [OpenCode serve](https://www.opencodecn.com/docs/server) as the local LLM server.

**Install OpenCode (if not already installed):**
```bash
# Follow installation instructions at https://www.opencodecn.com/
```

**Start the server:**
```bash
# The SDK uses port 54321 by default
opencode serve
```

The server will be available at `http://localhost:54321` by default.

### 2. Install Dependencies

The project uses [uv](https://docs.astral.sh/uv/) for Python dependency management.

**Backend:**
```bash
uv sync
```

Alternatively, you can use pip:
```bash
pip install -r pyproject.toml  # Or install directly: pip install opencode-ai fastapi uvicorn python-dotenv httpx pydantic
```

**Frontend:**
```bash
cd frontend
npm install
cd ..
```

### 3. Configure Environment

Create a `.env` file in the project root:

```bash
# OpenCode serve URL (defaults to http://localhost:54321 if not set)
OPENCODE_SERVER_URL=http://localhost:54321
```

### 4. Configure Models (Optional)

Edit `backend/config.py` to customize the council:

```python
COUNCIL_MODELS = [
    "openai:gpt-4",
    "anthropic:claude-3-5-sonnet",
    "google:gemini-1.5-pro",
    "openai:gpt-4-turbo",
]

CHAIRMAN_MODEL = "openai:gpt-4"
```

**Model Format:** Use `provider:model` format (e.g., `openai:gpt-4`, `anthropic:claude-3-5-sonnet`)

**Important:** The LLM Council requires:
- **Minimum 2 council models** for meaningful peer review (more models provide better perspectives)
- **1 chairman model** to synthesize the final response (can be the same as one of the council models)

The default configuration includes 4 council models plus 1 chairman, which provides robust multi-perspective analysis.

## Running the Application

**Option 1: Use the start script**
```bash
./start.sh
```

**Option 2: Run manually**

Terminal 1 (Backend):
```bash
uv run python -m backend.main
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

Then open http://localhost:5173 in your browser.

## Tech Stack

- **Backend:** FastAPI (Python 3.10+), OpenCode serve with official Python SDK ([opencode-ai](https://github.com/anomalyco/opencode-sdk-python))
- **Frontend:** React + Vite, react-markdown for rendering
- **Storage:** JSON files in `data/conversations/`
- **Package Management:** uv for Python, npm for JavaScript

## Model Requirements

The LLM Council system is designed to work with multiple AI models to provide diverse perspectives:

### Minimum Requirements
- **At least 2 council models**: Required for Stage 2 peer review to be meaningful. With only 1 model, there's nothing to compare and rank.
- **1 chairman model**: Required for Stage 3 synthesis. Can be the same as one of the council models or a different model.

### How It Works
1. **Stage 1**: All council models independently respond to your query
2. **Stage 2**: Each council model anonymously reviews and ranks all responses (including its own)
3. **Stage 3**: The chairman model synthesizes insights from all responses and rankings into a final answer

### Recommendations
- **3-5 council models**: Provides good diversity while maintaining reasonable response times
- **Different model types**: Mix models from different providers (OpenAI, Anthropic, Google, etc.) for varied perspectives
- **Chairman selection**: Use a strong reasoning model as chairman (e.g., GPT-4, Claude 3.5 Sonnet, Gemini 1.5 Pro)

The default configuration uses 4 council models, which offers an excellent balance of diverse perspectives and practical performance.

## Architecture

### OpenCode Serve Integration

This application uses OpenCode serve as the local LLM server, which provides:
- **Single API** for multiple LLM providers (OpenAI, Anthropic, Google, etc.)
- **Local execution** with your own API keys
- **Session-based conversations** with message history
- **Official Python SDK** for type-safe API calls

### Official OpenCode SDK

The application uses the official [OpenCode Python SDK](https://github.com/anomalyco/opencode-sdk-python), providing:
- **Type-safe API calls** with full IDE support and autocomplete
- **Automatic serialization/deserialization** of requests and responses
- **Async/sync support** for flexible integration
- **Consistent error handling** and retry logic
- **Regular updates** from the OpenCode team

The SDK is automatically installed via pip when you run `uv sync` or install dependencies.
