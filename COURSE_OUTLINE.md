# Large Language Models in Practice — 4-Hour Course Outline

**Duration:** 4 hours (240 minutes)
**Format:** Lecture + Hands-On Labs
**Audience:** Engineers / developers comfortable with Python and a terminal
**Final Project:** A working chatbot powered by Rowboat + custom MCP tools

---

## Course Goal

Go from "what is an LLM?" to shipping a production-ready chatbot that uses
Model Context Protocol (MCP) tools to answer real questions — all running
locally with Rowboat as the multi-agent orchestration layer.

---

## Prerequisites (Complete Before Class)

- Python 3.11+ and `uv`: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Docker Desktop running
- Ollama installed with a model pulled:
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ollama pull llama3.1
  ```
- Node.js 18+ (required for Rowboat)
- Clone and set up the repo:
  ```bash
  git clone https://github.com/seefor/network-automation.git
  cd network-automation
  uv sync --all-extras
  cp .env.example .env
  ```

---

## Schedule at a Glance

| Block | Topic | Type | Time |
|-------|-------|------|------|
| 0 | Welcome & Environment Check | Orientation | 10 min |
| 1 | How LLMs Actually Work | Lecture | 25 min |
| 2 | Lab 1 — Hands-On with Ollama | Hands-On | 20 min |
| 3 | Prompt Engineering | Lecture | 20 min |
| 4 | Lab 2 — Prompt Crafting Workshop | Hands-On | 20 min |
| — | **BREAK** | — | 10 min |
| 5 | LLM APIs & Function Calling | Lecture | 20 min |
| 6 | Lab 3 — Call an LLM API in Python | Hands-On | 20 min |
| 7 | Model Context Protocol (MCP) | Lecture | 20 min |
| 8 | Lab 4 — Build an MCP Tool Server | Hands-On | 25 min |
| 9 | Rowboat: Multi-Agent Chatbot | Lecture + Demo | 15 min |
| 10 | Lab 5 — Wire It All Together | Hands-On | 15 min |
| — | **Total** | | **240 min** |

---

## Block 0 — Welcome & Environment Check (10 min)

**Objectives**
- Understand the learning arc of the day
- Confirm every student has a working environment

**Activities**
- Instructor walks through the course arc: understand → prompt → call → extend → ship
- Students verify their setup:
  ```bash
  ollama run llama3.1 "Say hello in one sentence"   # should respond
  python3 -c "import httpx; print('ok')"            # should print ok
  docker info                                        # should not error
  ```
- Brief tour of what we'll build: a Rowboat chatbot with live MCP tools

---

## Block 1 — How LLMs Actually Work (25 min)

**Learning Objectives**
- Describe how an LLM predicts the next token
- Explain context windows, temperature, and why hallucinations happen
- Know the difference between a base model and a chat/instruction model

**Topics**

1. **Tokenization** (5 min)
   - Text is split into tokens (not words); `"network" → ["net", "work"]`
   - Token limits define how much the model can "see" at once
   - Why long prompts cost more and can degrade quality

2. **Next-Token Prediction** (7 min)
   - LLMs are probability machines: P(next token | all previous tokens)
   - Temperature controls randomness: 0 = deterministic, 1+ = creative
   - Top-P / top-K sampling and when to tune them

3. **Training vs. Inference** (5 min)
   - Pre-training: learn language patterns from the internet
   - Fine-tuning / RLHF: teach the model to follow instructions
   - Why a base model and a chat model behave so differently

4. **Context Window & Memory** (5 min)
   - Everything in the context window = the model's "working memory"
   - LLMs have no persistent memory across sessions (unless you build it)
   - RAG (Retrieval-Augmented Generation) as a teaser for the MCP section

5. **Hallucinations & Confidence** (3 min)
   - Confident ≠ correct
   - Most dangerous when asked about obscure facts or recent events
   - Mitigation: ground the model with tools (foreshadows MCP)

---

## Block 2 — Lab 1: Hands-On with Ollama (20 min)

**Goal:** Develop intuition for how model parameters and prompt structure
change model output.

**Exercises (run in terminal with `ollama run llama3.1`):**

| # | Exercise | What You're Testing |
|---|----------|---------------------|
| 1 | Ask a factual question with no context | Baseline hallucination risk |
| 2 | Same question but prepend "You are an expert in X" | Effect of system framing |
| 3 | Ask for a JSON object with specific fields | Structured output adherence |
| 4 | Set temperature to 0 via API, ask the same question twice | Determinism |
| 5 | Set temperature to 1.5 via API, ask again | Creativity / instability |
| 6 | Provide a fake "document" and ask questions about it | Grounding vs. parametric memory |

**Temperature experiment via Ollama API:**
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1",
  "prompt": "What is the capital of France?",
  "options": {"temperature": 0},
  "stream": false
}' | python3 -m json.tool
```

**Discussion:** Where did the model surprise you? When did it feel reliable?

---

## Block 3 — Prompt Engineering (20 min)

**Learning Objectives**
- Write prompts that produce consistent, usable output
- Apply the P.E.N.E. framework to structure complex prompts
- Use few-shot examples and chain-of-thought to improve accuracy

**Topics**

1. **System vs. User vs. Assistant Roles** (4 min)
   - `system`: sets the model's persona, rules, output format
   - `user`: the human's message
   - `assistant`: the model's reply (can be pre-filled for steering)
   - Most models are extremely sensitive to system prompt content

2. **The P.E.N.E. Framework** (8 min)
   - **P**urpose — be explicit: "Write a Python function that…"
   - **E**xamples — show one or two ideal input/output pairs (few-shot)
   - **N**uance — add constraints: "Use only stdlib, no third-party packages"
   - **E**xpertise — state the audience: "Assume the reader is a senior SRE"

3. **Chain-of-Thought (CoT)** (4 min)
   - "Think step by step before answering" reliably improves reasoning tasks
   - Scratchpad pattern: ask for reasoning in `<thinking>` tags, answer after
   - When NOT to use CoT: simple factual lookups, creative generation

4. **Output Format Control** (4 min)
   - JSON mode / structured outputs (supported by most APIs)
   - XML tags for multi-part responses: `<summary>` + `<code>` + `<tests>`
   - Asking the model to repeat constraints back to you as a sanity check

**Reference:** `milestone-2-copilot/lessons/02-prompt-engineering.md`

---

## Block 4 — Lab 2: Prompt Crafting Workshop (20 min)

**Goal:** Write prompts that reliably produce useful, structured output for
real engineering tasks.

**File:** `milestone-2-copilot/labs/lab01_prompt_crafting.md`

**Exercises:**

| # | Task | Skill |
|---|------|-------|
| 1 | Write a bad prompt → observe vague output | Baseline |
| 2 | Add Purpose + Nuance → compare output | P.E.N.E. |
| 3 | Add a few-shot example of the expected output format | Few-shot |
| 4 | Ask for JSON output with a specific schema | Structured output |
| 5 | Add CoT instruction → compare reasoning quality | Chain-of-thought |
| 6 | Write a system prompt that makes the model refuse off-topic questions | Guardrails |

**Challenge:** Write a single prompt that makes the model generate a Python
function, its docstring, and a pytest test — all in one response, correctly
formatted and runnable.

---

## --- BREAK (10 min) ---

---

## Block 5 — LLM APIs & Function Calling (20 min)

**Learning Objectives**
- Call a chat completions API programmatically from Python
- Define functions/tools that the model can decide to call
- Parse and act on tool-call responses in a loop

**Topics**

1. **Chat Completions API Shape** (5 min)
   ```python
   messages = [
       {"role": "system", "content": "You are a helpful assistant."},
       {"role": "user",   "content": "What is 2 + 2?"},
   ]
   response = client.chat.completions.create(
       model="llama3.1",
       messages=messages,
   )
   print(response.choices[0].message.content)
   ```
   - OpenAI-compatible API (works with Ollama, Anthropic, OpenAI, etc.)
   - `stream=True` for real-time token output

2. **Tool / Function Calling** (10 min)
   - Define a tool as a JSON Schema describing name, description, parameters
   - Model returns a `tool_calls` object instead of plain text when it decides to use a tool
   - Your code executes the function, appends the result, calls the API again
   - This loop continues until the model returns a final text response

   ```python
   tools = [{
       "type": "function",
       "function": {
           "name": "get_current_time",
           "description": "Returns the current UTC time as an ISO string",
           "parameters": {"type": "object", "properties": {}}
       }
   }]
   ```

3. **Agentic Loop Pattern** (5 min)
   ```
   user message
       → API call
       → tool_call? → execute → append result → API call again
       → text response → done
   ```
   - Safety: set a maximum iteration count to prevent infinite loops
   - This is the foundation Rowboat is built on

**Reference:** `milestone-2-copilot/lessons/03-ai-assisted-scripting.md`

---

## Block 6 — Lab 3: Call an LLM API in Python (20 min)

**Goal:** Build a minimal agentic loop in pure Python — no frameworks — so
you understand exactly what's happening under the hood.

**File:** `milestone-3-agentic/labs/lab01_hello_mcp/server.py` (reference)

**Exercises:**

```python
# Exercise 1: basic chat completions call
# TODO: call the Ollama OpenAI-compatible endpoint and print the reply

# Exercise 2: add a tool definition for "get_device_list"
# TODO: define the JSON Schema for a tool that takes no arguments
#       and returns a hardcoded list of device names

# Exercise 3: implement the agentic loop
# TODO: if response.choices[0].finish_reason == "tool_calls":
#       extract tool name + args, call your function, append result, loop

# Exercise 4: add a second tool "ping_device(hostname: str)"
# TODO: return a fake ping result; watch the model chain two tool calls
```

**Expected outcome:** A Python script where you can type a question in the
terminal, the model calls your tools as needed, and returns a grounded answer.

---

## Block 7 — Model Context Protocol (MCP) (20 min)

**Learning Objectives**
- Explain why MCP exists and what problem it solves
- Describe the client → server → tool call flow
- Build a tool with the FastMCP Python SDK

**Topics**

1. **The Problem MCP Solves** (4 min)
   - Without MCP: every app reimplements its own tool schema + transport
   - With MCP: a single open standard — any client talks to any server
   - Analogy: USB-C for AI tools

2. **MCP Architecture** (8 min)
   ```
   AI Client (Rowboat / Claude Desktop / your app)
       ↓  MCP protocol (JSON-RPC over stdio or SSE)
   MCP Server (your Python code)
       ↓  any backend (REST API, database, SSH, filesystem)
   Data / Services
   ```
   - **Tools**: functions the model can call (what we're building)
   - **Resources**: read-only data the model can access (files, URLs)
   - **Prompts**: reusable prompt templates exposed by the server
   - **Transport**: stdio for local processes, SSE for remote servers

3. **FastMCP SDK** (8 min)
   ```python
   from mcp.server.fastmcp import FastMCP

   mcp = FastMCP("my-server")

   @mcp.tool()
   def list_devices() -> list[str]:
       """Return all known device hostnames."""
       return ["switch-01", "switch-02", "switch-03"]

   @mcp.tool()
   def ping_device(hostname: str) -> dict:
       """Ping a device and return latency in ms."""
       return {"hostname": hostname, "latency_ms": 4.2, "status": "up"}

   if __name__ == "__main__":
       mcp.run()
   ```
   - The docstring becomes the tool description the model reads
   - Type hints become the JSON Schema parameters automatically
   - One decorator, one function — that's all it takes

**Reference:** `milestone-3-agentic/lessons/01-what-is-mcp.md`

---

## Block 8 — Lab 4: Build an MCP Tool Server (25 min)

**Goal:** Implement a real MCP server with multiple tools that a Rowboat
chatbot will call in the next lab.

**Files:**
- `milestone-3-agentic/labs/lab02_netbox_mcp/server.py` — starter skeleton
- `milestone-3-agentic/solutions/lab02_netbox_mcp/server.py` — reference

**Part A — Hello MCP (10 min)**

Start from the skeleton and implement three tools:

```python
# TODO 1: list_devices() → return hardcoded list of device names
# TODO 2: get_device_info(hostname: str) → return dict with ip, model, status
# TODO 3: check_connectivity(hostname: str) → return {"reachable": bool, "latency_ms": float}
```

Verify your tools are registered:
```bash
uv run python server.py --inspect
# should list: list_devices, get_device_info, check_connectivity
```

**Part B — Real Data Tools (15 min)**

Add two more tools that call real backends:

```python
# TODO 4: query_ip_addresses(prefix: str) → call NetBox REST API
#          GET /api/ipam/ip-addresses/?parent={prefix}
#          return list of {address, status, description}

# TODO 5: lookup_dns(hostname: str) → use Python socket.getaddrinfo()
#          return the resolved IP addresses
```

Test end-to-end:
```bash
make lab-up                          # start NetBox
uv run python server.py &            # run your MCP server
# use Claude Desktop or Rowboat to chat with it in the next lab
```

**Check your work:** `milestone-3-agentic/solutions/lab02_netbox_mcp/server.py`

---

## Block 9 — Rowboat: Multi-Agent Chatbot (15 min)

**Format:** Instructor demo + architecture explanation

**What is Rowboat?**

Rowboat is an open-source multi-agent orchestration platform. You describe
agents and their tools in YAML; Rowboat handles the routing, tool execution,
and multi-turn conversation loop — and gives you a polished chat UI out of
the box.

```
User message (chat UI)
    ↓
Rowboat Orchestrator
    ↓ picks the right agent
Specialized Agent (e.g., "Network Agent")
    ↓ decides which tools to call
MCP Server (your server.py from Lab 4)
    ↓
Real data (NetBox, DNS, devices...)
    ↑ tool results
Agent generates response
    ↑
User sees grounded answer in chat
```

**Why Rowboat + MCP?**
- Rowboat natively supports MCP servers as tool providers
- You write one MCP server; any Rowboat agent can use it
- Multi-agent: different agents can specialize (network agent, security agent, docs agent) and hand off to each other
- No framework lock-in — the MCP server is reusable everywhere

**Demo Walkthrough:**
1. Start Rowboat locally with Docker
2. Register the MCP server from Lab 4 as a tool provider
3. Define a "Network Assistant" agent in `rowboat.yml`
4. Chat: "Which IPs are allocated in 10.0.1.0/24 but unreachable?"
5. Watch Rowboat call `query_ip_addresses` + `check_connectivity` automatically
6. See the grounded, accurate answer in the chat UI

---

## Block 10 — Lab 5: Wire It All Together (15 min)

**Goal:** Connect your Lab 4 MCP server to Rowboat and have a working chatbot
by the end of class.

**Steps:**

1. **Start Rowboat**
   ```bash
   docker run -p 3000:3000 rowboathq/rowboat:latest
   # open http://localhost:3000
   ```

2. **Register your MCP server as a tool provider**

   In the Rowboat UI → Tools → Add MCP Server:
   ```
   Name:      network-tools
   Transport: stdio
   Command:   uv run python /path/to/lab02_netbox_mcp/server.py
   ```

3. **Create your agent** in the Rowboat UI → Agents → New Agent:
   ```yaml
   name: Network Assistant
   model: llama3.1          # or gpt-4o / claude-3-5-sonnet
   system_prompt: |
     You are a helpful network operations assistant.
     Use the available tools to answer questions about devices and IP addresses.
     Always base your answers on tool results, not assumptions.
   tools:
     - list_devices
     - get_device_info
     - query_ip_addresses
     - check_connectivity
   ```

4. **Chat with your bot** — try these prompts:
   - "List all the devices you know about"
   - "Which IPs are in the 10.0.1.0/24 prefix?"
   - "Is switch-01 reachable?"
   - "Give me a summary of the lab network"

5. **Extend (if time allows):** Add a second agent called "IP Auditor" that
   uses all 5 tools to find unreachable-but-allocated IPs and reports them.

---

## Learning Outcomes

By the end of this course you will be able to:

1. **Explain** how LLMs work: tokenization, inference, temperature, hallucinations
2. **Write effective prompts** using P.E.N.E., few-shot examples, and chain-of-thought
3. **Call LLM APIs** from Python and implement a basic agentic tool-calling loop
4. **Build an MCP server** that exposes real tools to any compatible AI client
5. **Deploy a Rowboat chatbot** with custom MCP tools and a working chat UI

---

## Quick Reference

```bash
# Ollama
ollama run llama3.1                       # interactive chat
ollama list                               # see downloaded models

# Ollama OpenAI-compatible API
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"llama3.1","messages":[{"role":"user","content":"Hello"}]}'

# MCP server
uv run python server.py --inspect         # list registered tools
uv run python server.py                   # run in stdio mode

# Rowboat
docker run -p 3000:3000 rowboathq/rowboat:latest
open http://localhost:3000

# Lab stack (optional — only needed if using NetBox tools)
make lab-up
make lab-status
```

---

*The pattern you learned today — LLM + tools via MCP + Rowboat orchestration —
scales from a lab chatbot all the way to production agentic systems.*
