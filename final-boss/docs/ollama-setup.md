# Setting Up Ollama for the Reclaim Agent

This guide walks you through installing and configuring Ollama so you can
run the Streamlit chat UI with a fully local LLM -- no API keys, no cloud
calls, everything on your machine.

## What Is Ollama?

Ollama is a local LLM runtime. It downloads, manages, and serves open-weight
models (Llama, Mistral, Qwen, etc.) on your laptop or workstation. It exposes
an API on `localhost:11434` that the Streamlit UI calls to get chat completions
with tool-calling support.

## Step 1: Install Ollama

### macOS

```bash
# Homebrew
brew install ollama

# Or direct download
curl -fsSL https://ollama.com/install.sh | sh
```

You can also download the macOS app from [ollama.com/download](https://ollama.com/download).

### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows

Download the installer from [ollama.com/download](https://ollama.com/download).

### Verify the installation

```bash
ollama --version
```

You should see a version number (e.g., `ollama version 0.5.x`).

## Step 2: Start the Ollama Server

```bash
ollama serve
```

This starts the API server on `http://localhost:11434`. Leave this terminal
open (or run it in the background). On macOS, the Ollama desktop app starts
the server automatically.

Verify it is running:

```bash
curl http://localhost:11434/api/tags
```

You should get a JSON response listing any models you have pulled.

## Step 3: Pull a Model

For this course, we recommend **Llama 3.1 (8B)** -- it supports tool calling,
runs well on 16GB of RAM, and produces solid results for network automation
tasks.

```bash
ollama pull llama3.1
```

This downloads approximately 4.7 GB. It only needs to happen once.

### Alternative models

| Model | Size | RAM Needed | Tool Calling | Notes |
|-------|------|-----------|-------------|-------|
| `llama3.1` | 4.7 GB | 8-16 GB | Yes | **Recommended.** Good balance of quality and speed. |
| `llama3.1:70b` | 40 GB | 48+ GB | Yes | Much better reasoning but needs serious hardware. |
| `qwen2.5` | 4.4 GB | 8-16 GB | Yes | Strong at structured output and code. |
| `mistral` | 4.1 GB | 8-16 GB | Yes | Fast, good for simpler tasks. |

You can pull multiple models and switch between them by changing the
`OLLAMA_MODEL` environment variable.

### Verify the model works

```bash
ollama run llama3.1 "What is a /24 subnet?"
```

You should get a sensible answer about 256 addresses, 254 usable, etc.

## Step 4: Configure Environment Variables

Copy the example env file and set your Ollama preferences:

```bash
cp .env.example .env
```

The relevant variables:

```bash
# --- Ollama (Local LLM) ---
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API endpoint. Change if running on a remote machine. |
| `OLLAMA_MODEL` | `llama3.1` | The model to use for chat. Must be pulled first. |

## Step 5: Run the Streamlit UI

```bash
cd final-boss
uv run streamlit run src/reclaim_agent/ui.py
```

Or from the repo root:

```bash
make boss-streamlit
```

The sidebar should show a green "Ollama: http://localhost:11434" status
indicator. If it shows red, check that `ollama serve` is running.

## Troubleshooting

### "Cannot connect to Ollama"

- Is the server running? Run `ollama serve` in a separate terminal.
- Is something else using port 11434? Check with:
  ```bash
  lsof -i :11434
  ```
- If Ollama is running on a different machine, set `OLLAMA_HOST` to its
  address (e.g., `http://192.168.1.50:11434`).

### "Model not found"

- Did you pull the model? Run `ollama list` to see what is available.
- Check the spelling: `ollama pull llama3.1` (not `llama-3.1` or `llama3`).

### Slow responses

- The first request after pulling a model is slower (loading into memory).
  Subsequent requests are faster.
- If responses take more than 30 seconds, your hardware may be under-spec.
  Try a smaller model (`mistral` or `qwen2.5`).
- Make sure no other heavy processes are competing for RAM.

### Tool calls not working

- Not all models support tool calling. Stick with the recommended models
  in the table above.
- If the model ignores tools and just responds with text, try a different
  model or check that the `tools` parameter is being passed (look at the
  browser console for errors).

### GPU acceleration

Ollama uses GPU acceleration automatically when available:

- **macOS:** Apple Silicon (M1/M2/M3/M4) is used automatically via Metal.
- **Linux:** NVIDIA GPUs are supported. Install the NVIDIA Container Toolkit
  or ensure CUDA drivers are installed.
- **Windows:** NVIDIA GPUs are supported with current drivers.

Check GPU usage:

```bash
# macOS -- Activity Monitor shows GPU usage under "GPU History"
# Linux
nvidia-smi
```

## Using Ollama with Claude Desktop

Ollama and Claude Desktop serve different roles in this project:

- **Claude Desktop** connects directly to your MCP server via the MCP
  protocol (stdio). Claude handles the AI reasoning. No Ollama needed.
- **Streamlit UI** uses Ollama for the AI reasoning and handles MCP tool
  calls in application code.

You can use either or both -- the MCP server does not care which client
connects to it.
