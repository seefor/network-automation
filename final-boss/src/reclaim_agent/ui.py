"""
Streamlit Chat UI for the Reclaim Agent
========================================

A chat interface for interacting with the Reclaim Agent MCP server. This UI
acts as an MCP *client* -- it sends user messages to a local Ollama LLM with
tool definitions, translates tool-use responses into calls against the MCP
server, and displays the results in a chat interface.

Everything runs locally. No API keys required.

Run with:
    cd final-boss
    uv run streamlit run src/reclaim_agent/ui.py

Requires:
    - Ollama running locally (ollama serve)
    - A model pulled (e.g., ollama pull llama3.1)
    - The MCP server running (either as a subprocess or separately)
    - `streamlit` and `ollama` packages installed

Students: This file is a working skeleton. Look for TODO comments for areas
you can extend or improve. The core chat loop is functional -- focus on
understanding the tool-calling pattern before modifying anything.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from typing import Any

import streamlit as st
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
NETBOX_URL = os.getenv("NETBOX_URL", "http://localhost:8000")

# The system prompt tells the LLM what it can do and how to behave.
SYSTEM_PROMPT = """\
You are an AI network operations assistant specializing in IP address
lifecycle management. You have access to the following tools through
an MCP server connected to a live lab environment:

1. **query_netbox_prefixes** -- List IP prefixes registered in NetBox.
2. **query_netbox_addresses** -- List individual IP addresses in NetBox,
   optionally filtered by prefix.
3. **poll_device_arp** -- SSH into a network device and retrieve the ARP table.
4. **find_stale_ips** -- Cross-reference NetBox allocations against live ARP
   data to identify unused / stale IP addresses.
5. **generate_reclamation_report** -- Produce a structured reclamation report
   with the stale IPs and recommended actions.
6. **execute_reclamation** -- Mark stale IPs as deprecated in NetBox. This is
   a WRITE operation and MUST require human confirmation before execution.

When the user asks you to reclaim IPs, always:
- Start by querying NetBox for current allocations.
- Poll the relevant network devices for live ARP data.
- Cross-reference to find stale IPs.
- Present a report and ASK for confirmation before executing reclamation.

Be concise and professional. Use tables when presenting lists of IPs.
"""

# ---------------------------------------------------------------------------
# Tool definitions -- these mirror what the MCP server exposes
# ---------------------------------------------------------------------------
# Each tool definition follows the Ollama tool-use schema. These MUST match
# the tools your MCP server registers. If you add a tool to server.py, add
# its definition here too.

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "query_netbox_prefixes",
            "description": (
                "Query NetBox for IP prefixes. Returns a list of prefixes with their "
                "status, VLAN, site, and tenant information. Use this to understand "
                "what address space is managed."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by status: active, reserved, deprecated, container",
                        "enum": ["active", "reserved", "deprecated", "container"],
                    },
                    "site": {
                        "type": "string",
                        "description": "Filter by site slug (e.g., 'lab-site-1')",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_netbox_addresses",
            "description": (
                "Query NetBox for individual IP addresses. Optionally filter by parent "
                "prefix to see all allocations within a specific subnet."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "prefix": {
                        "type": "string",
                        "description": "Parent prefix to filter by (e.g., '10.0.1.0/24')",
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter by status: active, reserved, deprecated, dhcp",
                        "enum": ["active", "reserved", "deprecated", "dhcp"],
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "poll_device_arp",
            "description": (
                "SSH into a network device and retrieve its ARP table. Returns a list "
                "of ARP entries with IP address, MAC address, and interface. Use this "
                "to see which IPs are actually in use on the network."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "hostname": {
                        "type": "string",
                        "description": "Device hostname or management IP (e.g., 'switch-01')",
                    },
                },
                "required": ["hostname"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_stale_ips",
            "description": (
                "Cross-reference NetBox IP allocations against live ARP data to "
                "identify stale (unused) IP addresses. An IP is stale if it is "
                "marked active in NetBox but does NOT appear in any device ARP table."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "prefix": {
                        "type": "string",
                        "description": "The prefix to analyze (e.g., '10.0.1.0/24')",
                    },
                    "hostnames": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of device hostnames to poll for ARP data",
                    },
                },
                "required": ["prefix", "hostnames"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_reclamation_report",
            "description": (
                "Generate a structured reclamation report listing stale IPs and "
                "recommended actions. Returns a formatted report suitable for "
                "review before executing reclamation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "prefix": {
                        "type": "string",
                        "description": "The prefix that was analyzed",
                    },
                    "stale_ips": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of stale IP addresses to include in the report",
                    },
                },
                "required": ["prefix", "stale_ips"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_reclamation",
            "description": (
                "Execute IP reclamation by marking stale IPs as deprecated in NetBox. "
                "This is a WRITE operation. The human operator MUST confirm the list "
                "of IPs before this tool is called. Never call this without explicit "
                "user approval."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ip_addresses": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of IP addresses to mark as deprecated",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for reclamation (for audit log)",
                    },
                },
                "required": ["ip_addresses"],
            },
        },
    },
]


# ---------------------------------------------------------------------------
# MCP Server communication
# ---------------------------------------------------------------------------

def call_mcp_tool(tool_name: str, tool_input: dict[str, Any]) -> str:
    """
    Execute a tool call against the MCP server.

    This skeleton uses subprocess to invoke the MCP server's tool handler
    directly. In a production setup you would use the MCP Python SDK's
    client transport (stdio or SSE) to communicate with a running server.

    TODO: Replace this with a proper MCP client session using the `mcp` SDK.
          Example:
              from mcp import ClientSession, StdioServerParameters
              async with ClientSession(StdioServerParameters(...)) as session:
                  result = await session.call_tool(tool_name, tool_input)

    For now, we use a simple HTTP call to a running MCP server or fall back
    to a subprocess invocation.
    """
    import httpx

    # --- Option A: HTTP call to an SSE/HTTP MCP server ---
    mcp_server_url = os.getenv("MCP_SERVER_URL", "")
    if mcp_server_url:
        try:
            response = httpx.post(
                f"{mcp_server_url}/call-tool",
                json={"name": tool_name, "arguments": tool_input},
                timeout=30.0,
            )
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        except httpx.HTTPError as exc:
            return json.dumps({"error": f"MCP server HTTP error: {exc}"})

    # --- Option B: stdio subprocess call ---
    try:
        payload = json.dumps({"tool": tool_name, "arguments": tool_input})
        result = subprocess.run(
            [
                sys.executable, "-m", "reclaim_agent.server",
                "--call-tool", payload,
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        )
        if result.returncode != 0:
            return json.dumps({
                "error": f"Tool execution failed: {result.stderr.strip() or 'unknown error'}"
            })
        return result.stdout.strip() or json.dumps({"result": "Tool executed successfully"})
    except subprocess.TimeoutExpired:
        return json.dumps({"error": "Tool execution timed out after 30 seconds"})
    except FileNotFoundError:
        return json.dumps({
            "error": (
                "Could not find the MCP server module. Make sure reclaim-agent "
                "is installed: uv pip install -e ."
            )
        })


# ---------------------------------------------------------------------------
# Human-in-the-Loop confirmation
# ---------------------------------------------------------------------------

def request_hitl_approval(ip_addresses: list[str], reason: str | None = None) -> bool:
    """
    Display a confirmation dialog for the execute_reclamation tool.

    This is the critical Human-in-the-Loop (HITL) gate. The AI MUST NOT
    execute reclamation without explicit human approval through this dialog.

    Returns True if the user approves, False otherwise.
    """
    st.warning("The AI wants to execute IP reclamation. Please review:")

    st.markdown("**IPs to be marked as deprecated:**")
    for ip in ip_addresses:
        st.markdown(f"- `{ip}`")

    if reason:
        st.markdown(f"**Reason:** {reason}")

    st.markdown(f"**Total:** {len(ip_addresses)} IP address(es)")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Approve Reclamation", type="primary", key="approve_reclaim"):
            return True
    with col2:
        if st.button("Reject", type="secondary", key="reject_reclaim"):
            return False

    return None  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Ollama API interaction
# ---------------------------------------------------------------------------

def get_ollama_client():
    """Create and cache the Ollama client."""
    try:
        import ollama
    except ImportError:
        st.error(
            "The `ollama` package is not installed. "
            "Run: `uv pip install ollama`"
        )
        st.stop()

    client = ollama.Client(host=OLLAMA_HOST)

    # Verify connectivity
    try:
        client.list()
    except Exception:
        st.error(
            f"Cannot connect to Ollama at {OLLAMA_HOST}. "
            "Make sure Ollama is running: `ollama serve`"
        )
        st.stop()

    return client


def send_message(client, messages: list[dict]) -> dict:
    """
    Send a message to Ollama and return the response.

    Uses the Ollama chat API with tool definitions so the model can
    request tool calls.
    """
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    response = client.chat(
        model=OLLAMA_MODEL,
        messages=full_messages,
        tools=TOOLS,
    )
    return response


def process_tool_calls(client, response, messages: list[dict]) -> tuple[str, list[dict]]:
    """
    Process the agentic tool-calling loop.

    When the LLM's response contains tool_calls, we:
    1. Extract the tool name and input
    2. Execute the tool (with HITL gate for execute_reclamation)
    3. Send the result back to the LLM
    4. Repeat until the LLM gives a final text response

    This is the core agentic loop pattern.

    TODO: Add retry logic for transient failures.
    TODO: Add a maximum iteration count to prevent infinite loops.
    TODO: Support parallel tool calls.
    """
    max_iterations = 10  # Safety valve
    iteration = 0
    tool_call_log: list[dict] = []

    while response.message.tool_calls and iteration < max_iterations:
        iteration += 1

        # Append the assistant message (with tool calls) to conversation
        messages.append(response.message.model_dump())

        for tool_call in response.message.tool_calls:
            tool_name = tool_call.function.name
            tool_input = tool_call.function.arguments

            tool_call_log.append({
                "tool": tool_name,
                "input": tool_input,
                "iteration": iteration,
            })

            # --- HITL gate for execute_reclamation ---
            if tool_name == "execute_reclamation":
                approval_key = f"approval_{iteration}_{tool_name}"

                if approval_key not in st.session_state:
                    st.session_state[approval_key] = "pending"
                    st.session_state["pending_reclamation"] = {
                        "approval_key": approval_key,
                        "ip_addresses": tool_input.get("ip_addresses", []),
                        "reason": tool_input.get("reason", "Not specified"),
                        "messages": [m for m in messages],
                    }
                    st.rerun()

                approval_status = st.session_state.get(approval_key, "pending")

                if approval_status == "approved":
                    result_text = call_mcp_tool(tool_name, tool_input)
                    tool_call_log[-1]["result"] = result_text
                elif approval_status == "rejected":
                    result_text = json.dumps({
                        "status": "rejected",
                        "message": "The human operator rejected this reclamation.",
                    })
                    tool_call_log[-1]["result"] = result_text
                else:
                    result_text = json.dumps({
                        "status": "pending",
                        "message": "Awaiting human approval.",
                    })
                    tool_call_log[-1]["result"] = result_text
            else:
                # Regular tool -- execute immediately
                result_text = call_mcp_tool(tool_name, tool_input)
                tool_call_log[-1]["result"] = result_text

            # Append tool result to conversation
            messages.append({
                "role": "tool",
                "content": result_text,
            })

        # Send the tool results back to the LLM for the next step
        response = send_message(client, messages)

    # Extract the final text response
    final_text = response.message.content or ""

    # Append the final assistant response
    messages.append({"role": "assistant", "content": final_text})

    return final_text, tool_call_log


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------

def render_sidebar():
    """Render the sidebar with connection status and configuration."""
    with st.sidebar:
        st.title("Reclaim Agent")
        st.caption("AI-Powered IP Reclamation")

        st.divider()

        st.subheader("Connection Status")

        # NetBox status
        netbox_ok = check_netbox_status()
        if netbox_ok:
            st.success(f"NetBox: {NETBOX_URL}", icon=None)
        else:
            st.error(f"NetBox: {NETBOX_URL} (unreachable)")

        # Ollama status
        ollama_ok = check_ollama_status()
        if ollama_ok:
            st.success(f"Ollama: {OLLAMA_HOST}")
        else:
            st.error(f"Ollama: {OLLAMA_HOST} (unreachable)")

        # MCP server status
        mcp_url = os.getenv("MCP_SERVER_URL", "")
        if mcp_url:
            st.info(f"MCP Server: {mcp_url}")
        else:
            st.info("MCP Server: subprocess mode")

        st.divider()

        st.subheader("Configuration")
        st.text_input("Model", value=OLLAMA_MODEL, disabled=True, key="model_display")

        # TODO: Add a dropdown to select from available Ollama models
        # TODO: Add temperature slider

        st.divider()

        st.subheader("Quick Actions")
        if st.button("Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.display_messages = []
            keys_to_remove = [
                k for k in st.session_state if k.startswith("approval_")
            ]
            for k in keys_to_remove:
                del st.session_state[k]
            if "pending_reclamation" in st.session_state:
                del st.session_state["pending_reclamation"]
            st.rerun()

        # TODO: Add "Export conversation" button
        # TODO: Add "Sample queries" with pre-filled prompts

        st.divider()
        st.caption("Built for the AI-Powered Network Automation course")


def check_netbox_status() -> bool:
    """Check if NetBox is reachable."""
    try:
        import httpx
        resp = httpx.get(f"{NETBOX_URL}/api/", timeout=3.0)
        return resp.status_code == 200
    except Exception:
        return False


def check_ollama_status() -> bool:
    """Check if Ollama is reachable."""
    try:
        import httpx
        resp = httpx.get(f"{OLLAMA_HOST}/api/tags", timeout=3.0)
        return resp.status_code == 200
    except Exception:
        return False


def render_tool_calls(tool_call_log: list[dict]):
    """Render tool calls in expandable sections so students can inspect them."""
    if not tool_call_log:
        return

    with st.expander(f"Tool Calls ({len(tool_call_log)} executed)", expanded=False):
        for i, call in enumerate(tool_call_log, 1):
            st.markdown(f"**{i}. `{call['tool']}`**")

            st.markdown("*Input:*")
            st.code(json.dumps(call["input"], indent=2), language="json")

            if "result" in call:
                st.markdown("*Result:*")
                try:
                    parsed = json.loads(call["result"])
                    st.code(json.dumps(parsed, indent=2), language="json")
                except (json.JSONDecodeError, TypeError):
                    st.code(str(call["result"]))

            if i < len(tool_call_log):
                st.divider()


def render_approval_dialog():
    """
    Render the HITL approval dialog if there is a pending reclamation.

    This is separated from the main chat loop so it persists across reruns.
    """
    pending = st.session_state.get("pending_reclamation")
    if not pending:
        return

    approval_key = pending["approval_key"]

    if st.session_state.get(approval_key) != "pending":
        return

    st.divider()
    st.subheader("Human Approval Required")
    st.warning(
        "The AI wants to execute IP reclamation. Review the following IPs "
        "and approve or reject the operation."
    )

    ip_addresses = pending["ip_addresses"]
    reason = pending["reason"]

    st.markdown("**IPs to mark as deprecated:**")
    for ip in ip_addresses:
        st.markdown(f"- `{ip}`")

    st.markdown(f"**Reason:** {reason}")
    st.markdown(f"**Count:** {len(ip_addresses)} address(es)")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "Approve Reclamation",
            type="primary",
            key="hitl_approve",
            use_container_width=True,
        ):
            st.session_state[approval_key] = "approved"
            del st.session_state["pending_reclamation"]
            st.rerun()

    with col2:
        if st.button(
            "Reject",
            type="secondary",
            key="hitl_reject",
            use_container_width=True,
        ):
            st.session_state[approval_key] = "rejected"
            del st.session_state["pending_reclamation"]
            st.rerun()


def main():
    """Main Streamlit application entry point."""
    st.set_page_config(
        page_title="Reclaim Agent",
        page_icon="<>",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ---- Initialize session state ----
    if "messages" not in st.session_state:
        # messages: the full Ollama API conversation (includes tool calls)
        st.session_state.messages = []
    if "display_messages" not in st.session_state:
        # display_messages: simplified list for rendering in the chat UI
        st.session_state.display_messages = []

    # ---- Sidebar ----
    render_sidebar()

    # ---- Main chat area ----
    st.title("Operation Reclaim")
    st.caption(
        "AI-powered IP address reclamation agent. Ask me to find stale IPs, "
        "generate reports, or reclaim unused addresses."
    )

    # Render conversation history
    for msg in st.session_state.display_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "tool_calls" in msg:
                render_tool_calls(msg["tool_calls"])

    # Render HITL dialog if pending
    render_approval_dialog()

    # ---- Chat input ----
    user_input = st.chat_input(
        "Ask about IP allocations, stale addresses, or reclamation..."
    )

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.display_messages.append({
            "role": "user",
            "content": user_input,
        })

        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
        })

        # ---- Call Ollama and process the response ----
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                client = get_ollama_client()

                try:
                    response = send_message(client, st.session_state.messages)

                    if response.message.tool_calls:
                        # Enter the tool-calling loop
                        final_text, tool_call_log = process_tool_calls(
                            client, response, st.session_state.messages
                        )
                        st.markdown(final_text)
                        render_tool_calls(tool_call_log)

                        st.session_state.display_messages.append({
                            "role": "assistant",
                            "content": final_text,
                            "tool_calls": tool_call_log,
                        })
                    else:
                        # Simple text response -- no tools needed
                        text = response.message.content or ""
                        st.markdown(text)

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": text,
                        })
                        st.session_state.display_messages.append({
                            "role": "assistant",
                            "content": text,
                        })

                except Exception as exc:
                    error_msg = f"Error communicating with Ollama: {exc}"
                    st.error(error_msg)
                    st.session_state.display_messages.append({
                        "role": "assistant",
                        "content": f"*Error: {error_msg}*",
                    })


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
