# AI-Powered Network Automation Course

A hands-on learning path that transitions network engineers from **imperative scripting** to **agentic automation** using AI, MCP, and modern APIs.

## Learning Path

| Milestone | Focus | You Will Build |
|-----------|-------|---------------|
| [1 - Manual Era](milestone-1-manual/) | REST APIs, CURL, Python `requests` | Scripts that talk to NetBox and network devices |
| [2 - Co-Pilot Era](milestone-2-copilot/) | LLM-assisted development | AI-generated audit scripts using prompt engineering |
| [3 - Agentic Era](milestone-3-agentic/) | MCP servers, tool-use, HITL | A local MCP server the AI can use to query your network |
| [Final Boss](final-boss/) | Full agentic workflow | An IP reclamation agent with human approval gates |

## Prerequisites

- Basic understanding of IP addressing and SSH
- A modern laptop (8GB+ RAM)
- Software: VS Code, Docker, `uv` (Python package manager)
- Ollama installed locally (free, no API key needed) — see [Ollama Setup Guide](final-boss/docs/ollama-setup.md)

## Quick Start

```bash
# 1. Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install Ollama (local LLM runtime)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1

# 3. Clone and enter the repo
git clone https://github.com/seefor/network-automation.git
cd network-automation

# 4. Create virtual environment and install dependencies
uv sync --all-extras

# 5. Copy environment config
cp .env.example .env

# 6. Start the lab environment
make lab-up

# 7. Verify everything is running
make lab-status
```

## Python Environment

This project uses `uv` for fast, reliable Python environment management. All
dependencies are defined in `pyproject.toml` at the repo root.

```bash
# Install all dependencies (creates .venv automatically)
uv sync --all-extras

# Or install without dev dependencies
uv sync

# Activate the virtual environment (optional - uv run handles this)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### What gets installed

| Package | Purpose |
|---------|---------|
| `httpx`, `requests` | HTTP clients for API calls |
| `netmiko`, `napalm` | Network device automation |
| `pynetbox` | NetBox API client |
| `mcp` | Model Context Protocol SDK |
| `ollama` | Ollama Python client |
| `streamlit` | Chat UI framework |
| `pydantic` | Data validation |
| `rich` | Terminal formatting |
| `pytest`, `ruff` | Testing and linting (dev) |

## Tech Stack

- **Language:** Python 3.11+ (managed with `uv`)
- **AI Protocol:** Model Context Protocol (MCP) via Python SDK
- **Network Targets:** Arista cEOS (Containerlab) + NetBox v3.7 (Source of Truth)
- **AI Runtime:** Ollama (local LLMs — no API key required)
- **AI Interface:** Claude Desktop (MCP Client) or custom Streamlit UI (Ollama-powered)

## Lab Environment

The lab runs NetBox v3.7 and Arista cEOS containers. NetBox is pinned to v3.7
for stable API token authentication (v4.0 changed the token format).

| Service | URL | Credentials |
|---------|-----|-------------|
| NetBox UI | http://localhost:8000 | `admin` / `admin` |
| NetBox API Token | (pre-configured) | `0123456789abcdef0123456789abcdef01234567` |
| cEOS Switches | SSH via Containerlab | `admin` / `admin` |

The API token is automatically created on first boot — no manual setup required.

## Project Structure

```
network-automation/
├── milestone-1-manual/      # REST fundamentals
├── milestone-2-copilot/     # LLM-assisted scripting
├── milestone-3-agentic/     # MCP basics
├── final-boss/              # Graduation project
│   ├── src/reclaim_agent/   # MCP server skeleton
│   ├── docs/                # Setup guides (Ollama, Claude Desktop)
│   └── tests/               # Test suite
├── shared/                  # Shared Docker configs & scripts
├── pyproject.toml           # Python dependencies (uv/pip)
├── Makefile                 # Lab orchestration commands
└── .env.example             # Environment variable template
```
