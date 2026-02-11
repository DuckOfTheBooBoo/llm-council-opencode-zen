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
# Local only (default, binds to 127.0.0.1:4096)
opencode serve

# Or for network access (accessible from other machines/containers)
opencode serve --hostname 0.0.0.0 --port 4096
```

**Optional: Enable HTTP Basic Auth:**
```bash
export OPENCODE_SERVER_PASSWORD=your_password
export OPENCODE_SERVER_USERNAME=opencode  # Optional, defaults to "opencode"
opencode serve
```

The server will be available at `http://127.0.0.1:4096` by default.

### 2. Generate OpenAPI Client

The application uses a Python client generated from OpenCode serve's OpenAPI specification.

**Generate the client:**
```bash
./generate_openapi_client.sh
```

This script will:
1. Fetch the OpenAPI spec from your running `opencode serve` instance
2. Generate a Python client using Docker and openapi-generator
3. Place the generated client in `opencode_client/` directory

**Note:** The generated client directory is excluded from git. Regenerate as needed.

### 3. Install Dependencies

The project uses [uv](https://docs.astral.sh/uv/) for Python dependency management.

**Backend:**
```bash
uv sync
```

**Frontend:**
```bash
cd frontend
npm install
cd ..
```

### 4. Configure Environment

Create a `.env` file in the project root:

```bash
# OpenCode serve URL (defaults to http://127.0.0.1:4096 if not set)
OPENCODE_SERVER_URL=http://127.0.0.1:4096

# Optional HTTP Basic Auth (leave empty if not using auth)
OPENCODE_SERVER_USERNAME=opencode
OPENCODE_SERVER_PASSWORD=
```

### 5. Configure Models (Optional)

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

- **Backend:** FastAPI (Python 3.10+), OpenCode serve with OpenAPI-generated client
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
- **OpenAPI 3.1 specification** for type-safe client generation

### Generated Client

The Python client is generated from OpenCode serve's OpenAPI spec, providing:
- **Type-safe API calls** with full IDE support
- **Automatic serialization/deserialization** of requests and responses
- **Built-in authentication** support (HTTP Basic Auth)
- **Consistent error handling**

To regenerate the client (e.g., after server updates):
```bash
./generate_openapi_client.sh
```
