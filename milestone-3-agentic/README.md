# Milestone 3: The "Agentic" Era

## The Shift: From "AI Writes Code" to "AI Executes Actions"

In Milestone 1, you wrote Python scripts by hand. In Milestone 2, you used AI to
*help you write* those scripts. Now we cross a fundamental line: **the AI doesn't
just write code -- it runs it.**

This is the difference between asking ChatGPT to "write me a script that checks
interface status" and asking Claude to "check the status of interface Gi0/0/1 on
switch-core-01." In the first case, you copy-paste-run. In the second, the AI
reaches into your network and pulls the answer back itself.

This is what "agentic" means. The AI has **agency** -- the ability to take actions
in real systems on your behalf.

## What Makes This Possible: MCP

The **Model Context Protocol (MCP)** is the bridge between AI models and your
infrastructure. Think of it as a standardized way to give an AI model hands and
eyes -- tools it can call to read data, make changes, and interact with the real
world.

You will build MCP servers that expose network operations as tools. The AI
discovers those tools, understands what they do from their descriptions, and calls
them when appropriate.

## What You Will Build

| Lab | What It Does |
|-----|-------------|
| **Lab 01: Hello MCP** | A minimal MCP server with mock network tools. Your first server. |
| **Lab 02: NetBox MCP** | An MCP server connected to a real NetBox instance. Live data. |

## Lessons

| # | Topic | Key Concept |
|---|-------|-------------|
| 01 | What is MCP? | Architecture, protocol, why it exists |
| 02 | Building an MCP Server | Python SDK, tools, schemas, transport |
| 03 | Human-in-the-Loop | Why AI must never make changes without approval |

## Prerequisites

- Completed Milestone 1 (you understand Netmiko, NAPALM, network automation basics)
- Completed Milestone 2 (you understand prompting, structured output, AI-assisted workflows)
- Python 3.11+
- `uv` package manager installed

## The Golden Rule

**Read operations are free. Write operations require human approval. Always.**

An AI that can read interface status is useful. An AI that can push config changes
without asking is a career-ending event. Every tool you build in this milestone
will respect this boundary.

## Directory Structure

```
milestone-3-agentic/
  lessons/
    01-what-is-mcp.md
    02-building-mcp-server.md
    03-hitl-pattern.md
  labs/
    lab01_hello_mcp/
      server.py
      pyproject.toml
    lab02_netbox_mcp/
      server.py
      pyproject.toml
  solutions/
    lab01_hello_mcp/
      server.py
    lab02_netbox_mcp/
      server.py
```
