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
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Ollama (local LLM runtime)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1

# Clone and enter the repo
git clone https://github.com/seefor/network-automation && cd network-automation

# Start the lab environment
make lab-up

# Verify everything is running
make lab-status
```

## Tech Stack

- **Language:** Python 3.11+ (managed with `uv`)
- **AI Protocol:** Model Context Protocol (MCP) via Python SDK
- **Network Targets:** Arista cEOS (Containerlab) + NetBox (Source of Truth)
- **AI Runtime:** Ollama (local LLMs — no API key required)
- **AI Interface:** Claude Desktop (MCP Client) or custom Streamlit UI (Ollama-powered)

## Project Structure

```
network-automation/
├── milestone-1-manual/      # REST fundamentals
├── milestone-2-copilot/     # LLM-assisted scripting
├── milestone-3-agentic/     # MCP basics
├── final-boss/              # Graduation project
│   ├── src/reclaim_agent/   # MCP server skeleton
│   ├── lab/                 # Docker + Containerlab configs
│   └── tests/               # Test suite
├── shared/                  # Shared Docker configs & scripts
├── Makefile                 # Lab orchestration commands
└── .env.example             # Environment variable template
```
