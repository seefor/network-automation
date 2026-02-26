# AI-Powered Network Automation — 4-Hour Course Outline

**Duration:** 4 hours (240 minutes)
**Format:** Lecture + Hands-On Labs
**Audience:** Network engineers with basic Python/CLI exposure
**Environment:** Local Docker lab (NetBox + 3 Arista switch emulators + Ollama)

---

## Course Goal

Take you from manually clicking NetBox to running an autonomous AI agent that
audits your network, finds stale IP allocations, and reclaims them — all with a
human-approval gate before anything changes.

---

## Prerequisites (Complete Before Class)

- Docker Desktop running
- `uv` installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Ollama installed with `llama3.1` pulled: `ollama pull llama3.1`
- Repo cloned and environment ready:

```bash
git clone https://github.com/seefor/network-automation.git
cd network-automation
uv sync --all-extras
cp .env.example .env
make lab-up        # starts NetBox + 3 switches
make lab-status    # verify everything is green
```

---

## Schedule at a Glance

| Block | Topic | Type | Time |
|-------|-------|------|------|
| 0 | Welcome & Lab Check | Orientation | 10 min |
| 1 | REST APIs + NetBox | Lecture | 25 min |
| 2 | Lab 1 — curl the Network | Hands-On | 25 min |
| 3 | Python Requests | Lecture | 10 min |
| 4 | Lab 2 — Python CRUD | Hands-On | 25 min |
| — | **BREAK** | — | 10 min |
| 5 | LLMs as Co-Pilots | Lecture | 20 min |
| 6 | Lab 3 — Prompt Engineering + Audit Script | Hands-On | 25 min |
| 7 | Model Context Protocol (MCP) | Lecture | 25 min |
| 8 | Lab 4 — Build Your First MCP Server | Hands-On | 25 min |
| 9 | Final Boss Demo + Architecture Review | Lecture/Demo | 20 min |
| — | **Total** | | **240 min** |

---

## Block 0 — Welcome & Lab Check (10 min)

**Objectives**
- Understand the learning arc: Manual → Co-Pilot → Agentic
- Confirm every student has a working lab environment

**Activities**
- Instructor overview of the 4 milestones and the "Final Boss" capstone
- Students run `make lab-status` and confirm NetBox is reachable at `http://localhost:8000`
- Quick tour of the NetBox UI (admin/admin) and the three emulated switches

---

## Block 1 — REST APIs & NetBox as Source of Truth (25 min)

**Learning Objectives**
- Explain what a REST API is and why they matter in network automation
- Map HTTP verbs (GET, POST, PUT, PATCH, DELETE) to Create/Read/Update/Delete
- Understand why NetBox is the authoritative source of truth for IP and device data

**Topics**

1. **What is an API?** (5 min)
   - Client-server communication over HTTP
   - Request = verb + URL + optional body; Response = status code + JSON
   - Authentication via bearer tokens

2. **REST Conventions** (8 min)
   - Stateless requests, uniform interface
   - HTTP status codes that matter: 200, 201, 204, 400, 401, 404
   - Pagination: `limit` / `offset` pattern

3. **NetBox in 5 Minutes** (7 min)
   - DCIM (devices, racks, sites) vs. IPAM (prefixes, IP addresses, VRFs)
   - Concept of "source of truth" vs. "configuration management"
   - API token generation in the UI

4. **Reading the Docs** (5 min)
   - How to find an endpoint in the NetBox Swagger UI (`/api/schema/swagger-ui/`)
   - Inspecting live requests in the NetBox UI (Network tab)

**Reference:** `milestone-1-manual/lessons/01-what-is-an-api.md`

---

## Block 2 — Lab 1: curl the Network (25 min)

**Goal:** Interact with a live NetBox API using nothing but `curl` and your terminal.

**File:** `milestone-1-manual/labs/lab01_curl_netbox.sh`

**Exercises (work through in order):**

| # | Task | Verb | Endpoint |
|---|------|------|----------|
| 1 | List all sites | GET | `/api/dcim/sites/` |
| 2 | List all devices | GET | `/api/dcim/devices/` |
| 3 | Filter devices by site | GET | `/api/dcim/devices/?site=lab` |
| 4 | Get a single device by ID | GET | `/api/dcim/devices/{id}/` |
| 5 | List all IP prefixes | GET | `/api/ipam/prefixes/` |
| 6 | List IPs in the 10.0.1.0/24 prefix | GET | `/api/ipam/ip-addresses/?parent=10.0.1.0/24` |
| 7 | Create a new IP address | POST | `/api/ipam/ip-addresses/` |
| 8 | Update its description | PATCH | `/api/ipam/ip-addresses/{id}/` |
| 9 | Delete the IP you created | DELETE | `/api/ipam/ip-addresses/{id}/` |

**Key `curl` flags to know:**
```bash
-H "Authorization: Token $TOKEN"    # auth
-H "Content-Type: application/json" # for POST/PATCH
-d '{"key": "value"}'               # request body
-X PATCH                            # override HTTP verb
-s | python3 -m json.tool           # pretty-print JSON
```

**Check your work:** `solutions/lab01_curl_netbox.sh`

---

## Block 3 — Python Requests (10 min)

**Learning Objectives**
- Translate `curl` commands into Python using the `requests` library
- Handle pagination, error checking, and reusable session objects

**Topics**

1. **Requests Basics** (4 min)
   - `requests.get()`, `.post()`, `.patch()`, `.delete()`
   - `response.raise_for_status()` — never ignore HTTP errors
   - Passing headers via `session = requests.Session()`

2. **Pagination Pattern** (3 min)
   ```python
   while url:
       r = session.get(url, params={"limit": 50})
       data = r.json()
       results.extend(data["results"])
       url = data["next"]
   ```

3. **When to Use `pynetbox`** (3 min)
   - High-level SDK that wraps the REST API
   - Useful for complex filtering; raw `requests` is fine for simple scripts

**Reference:** `milestone-1-manual/lessons/02-curl-basics.md`, `lessons/03-python-requests.md`

---

## Block 4 — Lab 2: Python CRUD (25 min)

**Goal:** Rewrite the curl exercises as a Python script with proper error handling.

**File:** `milestone-1-manual/labs/lab02_python_requests.py`

**Exercises:**

| # | Task | Skill Practiced |
|---|------|-----------------|
| 1 | Create a `requests.Session` with auth token | Session setup |
| 2 | Fetch and print all devices as a table | Pagination + formatting |
| 3 | Find all IPs in `10.0.1.0/24` | Filtering |
| 4 | Create a new IP, update its status, delete it | Full CRUD lifecycle |
| 5 | Wrap everything in `try/except` with `raise_for_status` | Error handling |

**Bonus:** Use `rich` to render a pretty table of results.

**Check your work:** `solutions/lab02_python_requests.py`

---

## --- BREAK (10 min) ---

---

## Block 5 — LLMs as Your Co-Pilot (20 min)

**Learning Objectives**
- Understand how LLMs tokenize and predict text (not "thinking" — pattern completion)
- Apply the P.E.N.E. prompt engineering framework to get useful code
- Know when LLM output is trustworthy and when to validate it

**Topics**

1. **How LLMs Actually Work** (5 min)
   - Tokenization, next-token prediction, temperature
   - What a "context window" is and why it matters for long scripts
   - Hallucinations: confident + wrong (especially for obscure APIs)

2. **Prompt Engineering — P.E.N.E. Framework** (8 min)
   - **P**urpose: be explicit about the goal ("write a Python script that…")
   - **E**xamples: give a few-shot example of the API response format
   - **N**uance: specify constraints ("use `httpx`, not `requests`; async only")
   - **E**xpertise: tell the model your skill level / context
   - Chain-of-thought: "Think step by step before writing code"

3. **Using Ollama Locally** (4 min)
   - `ollama run llama3.1` — interactive chat in terminal
   - Why local models matter for network ops (no data leaves your environment)
   - Choosing the right model for the task: small+fast vs. large+smart

4. **Validation Strategies** (3 min)
   - Always test generated code against your lab before production
   - Ask the model to explain its logic line-by-line
   - Diff AI output against your own approach

**Reference:** `milestone-2-copilot/lessons/01-llm-fundamentals.md`, `lessons/02-prompt-engineering.md`

---

## Block 6 — Lab 3: Prompt Crafting + Device Audit Script (25 min)

**Goal:** Use an LLM to help complete a skeleton device audit script that SSHs into
all three switches and cross-references their ARP tables with NetBox.

**Files:**
- `milestone-2-copilot/labs/lab01_prompt_crafting.md` — prompt exercises
- `milestone-2-copilot/labs/lab02_audit_script.py` — skeleton to complete

**Part A — Prompt Crafting (10 min)**

Work through the prompts in `lab01_prompt_crafting.md`:
1. Write a bad prompt — observe vague output
2. Rewrite with P.E.N.E. — observe specific, usable output
3. Add few-shot examples of the NetBox IP JSON — observe accurate API calls
4. Ask for error handling — observe defensive code generation

**Part B — Complete the Audit Script (15 min)**

The skeleton in `lab02_audit_script.py` has `# TODO` markers. Use your LLM
(Ollama / Claude) to fill them in:

```python
# TODO: SSH to each switch and run "show ip arp"
# TODO: Parse ARP output into {ip: mac} dict
# TODO: Fetch all IPs from NetBox for 10.0.1.0/24
# TODO: Compare — find IPs that are in NetBox but NOT in any ARP table
# TODO: Print a summary report
```

**Expected output:**
```
Stale IPs found (in NetBox but not on network):
  10.0.1.50  — allocated, no ARP entry on any switch
  10.0.1.51  — allocated, no ARP entry on any switch
  ...
```

**Check your work:** `solutions/lab02_audit_script.py`

---

## Block 7 — Model Context Protocol (MCP) (25 min)

**Learning Objectives**
- Explain the MCP architecture and why it exists
- Describe how an AI model discovers and calls tools
- Implement the Human-in-the-Loop (HITL) approval pattern

**Topics**

1. **From Co-Pilot to Agent** (5 min)
   - Co-pilot: AI suggests → human executes
   - Agent: AI suggests AND executes → human approves
   - Why the distinction matters for network operations (blast radius)

2. **MCP Architecture** (10 min)
   - **Client**: the AI model (Claude Desktop, custom app)
   - **Server**: your Python code that exposes tools
   - **Transport**: stdio (subprocess) or SSE (HTTP)
   - **Tool schema**: JSON Schema describing inputs/outputs
   - Flow: `list_tools` → model picks tool → `call_tool` → model reads result → responds

   ```
   User Chat
      ↓
   AI Model (Claude / Ollama)
      ↓  MCP protocol (stdio)
   Your MCP Server (Python)
      ↓  REST / SSH
   NetBox + Network Devices
   ```

3. **FastMCP — Python SDK** (5 min)
   - `@mcp.tool()` decorator to register a function as a tool
   - Docstring becomes the tool description the model reads
   - Type hints become the JSON Schema automatically

   ```python
   @mcp.tool()
   def query_netbox_prefixes(site: str = "lab") -> list[dict]:
       """Return all IP prefixes for the given site."""
       ...
   ```

4. **Human-in-the-Loop Pattern** (5 min)
   - Problem: autonomous writes are dangerous
   - Solution: dry-run first, confirm second
   - Implementation: `confirmed: bool = False` parameter on write tools
   - First call → return preview; second call with `confirmed=True` → execute

**Reference:** `milestone-3-agentic/lessons/01-what-is-mcp.md`, `lessons/02-building-mcp-servers.md`, `lessons/03-hitl-pattern.md`

---

## Block 8 — Lab 4: Build Your First MCP Server (25 min)

**Goal:** Implement two MCP servers — a minimal hello-world, then a real one
that queries your live NetBox lab.

**Files:**
- `milestone-3-agentic/labs/lab01_hello_mcp/server.py`
- `milestone-3-agentic/labs/lab02_netbox_mcp/server.py`

**Part A — Hello MCP (10 min)**

Open `lab01_hello_mcp/server.py`. It has stubs for three mock tools:

```python
# TODO 1: Register a tool called "list_switches" that returns a hardcoded list
# TODO 2: Register a tool called "ping_switch" that takes an ip: str argument
# TODO 3: Register a tool called "get_switch_status" that returns uptime/load
```

Run your server and inspect the tool list:
```bash
uv run python lab01_hello_mcp/server.py --inspect
```

**Part B — NetBox MCP (15 min)**

Open `lab02_netbox_mcp/server.py`. Connect it to your live lab:

```python
# TODO 1: Implement query_prefixes() — GET /api/ipam/prefixes/
# TODO 2: Implement query_ip_addresses(prefix) — GET /api/ipam/ip-addresses/?parent=prefix
# TODO 3: Wire both tools into the MCP server with @mcp.tool()
```

Test via Ollama:
```bash
ollama run llama3.1 "What prefixes exist in my lab?"
# (with MCP server running via Claude Desktop or direct SDK call)
```

**Check your work:** `solutions/lab01_hello_mcp/server.py`, `solutions/lab02_netbox_mcp/server.py`

---

## Block 9 — Final Boss: Autonomous IP Reclamation Agent (20 min)

**Format:** Instructor demo + architecture walkthrough. Students receive the
capstone as a take-home project.

**The Mission**

Every network accumulates stale IP allocations — addresses marked "active" in
NetBox that haven't appeared in an ARP table in months. Build an agent that:

1. Queries NetBox for all IPs in a prefix
2. SSHs into all switches and collects ARP tables
3. Finds IPs that are allocated but invisible on the network
4. Generates a structured reclamation report
5. Deprecates stale IPs in NetBox — **only after you approve it**

**Live Demo Flow**
```
User: "Audit 10.0.1.0/24 and reclaim any stale IPs"

Agent → query_netbox_addresses("10.0.1.0/24")       # 11 IPs found
Agent → poll_device_arp("switch-01")                 # 3 live IPs
Agent → poll_device_arp("switch-02")                 # 2 live IPs
Agent → poll_device_arp("switch-03")                 # 1 live IP
Agent → find_stale_ips(...)                          # 5 stale IPs identified
Agent → generate_reclamation_report(...)

"I found 5 stale IPs: 10.0.1.50, .51, .52, .100, .101
 These are allocated in NetBox but absent from all ARP tables.
 Shall I deprecate them?"

User: "Yes, go ahead."

Agent → execute_reclamation(ips=[...], confirmed=True)

"Done. 5 IPs marked as deprecated in NetBox."
```

**The 6 Tools You'll Implement**

| Tool | Action | Safety |
|------|--------|--------|
| `query_netbox_prefixes` | List prefixes | Read-only |
| `query_netbox_addresses` | List IPs in prefix | Read-only |
| `poll_device_arp` | SSH → ARP table | Read-only |
| `find_stale_ips` | Compare allocations vs. live | Read-only |
| `generate_reclamation_report` | Structured JSON report | Read-only |
| `execute_reclamation` | Deprecate stale IPs | **Write + HITL gate** |

**Key Files for the Take-Home Capstone**
- `final-boss/src/reclaim_agent/server.py` — MCP server with 6 tool stubs
- `final-boss/src/reclaim_agent/tools/netbox.py` — async NetBox REST client
- `final-boss/src/reclaim_agent/tools/devices.py` — SSH device connector
- `final-boss/src/reclaim_agent/tools/analyzer.py` — stale IP comparison logic
- `final-boss/docs/project-spec.md` — full requirements + acceptance criteria

**Run the tests to validate your implementation:**
```bash
make boss-test
```

**Launch the Streamlit chat UI to interact with your agent:**
```bash
make boss-streamlit
# open http://localhost:8501
```

---

## Learning Outcomes

By the end of this course you will be able to:

1. **Query any REST API** with curl and Python, handling auth, pagination, and errors
2. **Use an LLM as a pair programmer** to write and explain network automation scripts
3. **Build an MCP server** that exposes network tools to any compatible AI model
4. **Design HITL approval gates** so automated agents cannot make changes without your sign-off
5. **Audit live network state** against a source of truth and generate actionable reports

---

## Quick Reference

```bash
# Lab management
make lab-up          # start Docker stack
make lab-down        # stop Docker stack
make lab-status      # check health
make lab-seed        # populate NetBox with test data

# Final boss
make boss-server     # run MCP server (stdio)
make boss-streamlit  # launch chat UI
make boss-test       # run pytest suite

# SSH into emulated switches (password: admin)
ssh admin@localhost -p 2201   # switch-01
ssh admin@localhost -p 2202   # switch-02
ssh admin@localhost -p 2203   # switch-03

# NetBox UI
open http://localhost:8000    # login: admin / admin
```

---

*Good luck — and remember: no automation tool should ever write to production
without a human in the loop.*
