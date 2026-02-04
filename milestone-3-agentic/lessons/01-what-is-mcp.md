# Lesson 01: What is MCP?

## The Problem

You have an AI model that knows everything about networking. It can explain BGP
path selection, write Jinja2 templates, and debug ACL logic. But it can't *do*
anything. It can't check if an interface is up. It can't query NetBox. It can't
pull a route table.

The model is a brain without hands.

**MCP gives it hands.**

## Model Context Protocol (MCP)

MCP is an open protocol that standardizes how AI models discover and call external
tools. It was created by Anthropic and released as an open standard. Any model that
supports tool calling can be an MCP client -- including local models via Ollama.

If you come from a networking background, the closest analogy is **SNMP**:

- SNMP exposes device data through OIDs. MCP exposes operations through **tools**.
- An SNMP manager discovers what a device can report. An MCP client discovers what
  a server can do.
- SNMP has GET (read) and SET (write). MCP tools can be read-only or read-write.
- The MIB describes the schema. MCP uses **JSON Schema** to describe tool inputs.

The difference: MCP tools are described in natural language, so an AI model can
understand *what they do* and *when to use them* without being explicitly programmed.

## Architecture

```
+------------------+          +------------------+          +------------------+
|                  |          |                  |          |                  |
|    AI Model      |          |   MCP Server     |          |   Your Network   |
|    (Client)      |<-------->|   (Python)       |<-------->|   Infrastructure |
|                  |   MCP    |                  |   API/   |                  |
|  Claude, GPT,    | Protocol |  Your code that  |   SSH/   |  NetBox, Routers |
|  local LLM       |          |  exposes tools   |   REST   |  Switches, etc.  |
|                  |          |                  |          |                  |
+------------------+          +------------------+          +------------------+
       ^                             ^
       |                             |
       |  1. "What tools do          |  3. Tool calls your
       |     you have?"              |     function, talks to
       |                             |     real infrastructure
       |  2. "Call get_interfaces    |
       |     on router-01"           |  4. Returns result
       |                             |     back to the model
```

### The Three Pieces

**1. MCP Client (the AI)**
The AI model or application that wants to use tools. Claude Desktop, a Streamlit
chat UI backed by Ollama, VS Code with Copilot, or any MCP-compatible app --
these are MCP clients. They speak the MCP protocol to discover and call tools.

**2. MCP Server (your code)**
A program you write that exposes tools. Each tool has a name, a description, and
an input schema. The server handles incoming tool calls and returns results.

**3. Tools (the operations)**
Individual functions that do something useful: query a device, check a prefix,
list VLANs. Each tool is a function with typed parameters and a return value.

## MCP vs Function Calling

You may have used "function calling" with OpenAI, Ollama, or other APIs. Here is
how MCP differs:

| Aspect | Function Calling | MCP |
|--------|-----------------|-----|
| **Scope** | Single API provider | Universal, open standard |
| **Discovery** | You define functions in each API call | Server advertises tools dynamically |
| **Transport** | HTTP to one API | stdio, SSE, or HTTP -- your choice |
| **Execution** | You run the function yourself | Server runs the function for you |
| **Reuse** | Tied to one model provider | Any MCP client works with any server |

With function calling, the model *suggests* a function call, and your application
code runs it. With MCP, the model *actually calls* the tool through the server.
You write the server once, and any MCP-compatible client can use it.

## Transport Layers

MCP supports multiple ways for the client and server to communicate:

### stdio (Standard I/O)
The client spawns the server as a subprocess. Communication happens over
stdin/stdout. This is the simplest and most common for local development.

```
Client  --stdin-->  Server Process  --stdout-->  Client
```

Best for: Local development, single-user setups, Claude Desktop, Ollama-backed chat UIs.

### SSE (Server-Sent Events)
The server runs as an HTTP service. The client connects over HTTP with
Server-Sent Events for streaming. Good for remote or multi-user deployments.

Best for: Shared servers, remote access, production deployments.

### Streamable HTTP
The newest transport. Uses standard HTTP POST for requests and optional SSE for
streaming responses. Simplest to deploy behind load balancers and proxies.

Best for: Production deployments, cloud hosting, API gateway integration.

## Tool Schema Format

Every MCP tool is defined by three things:

1. **Name** -- a short identifier (e.g., `get_interface_status`)
2. **Description** -- natural language explanation the AI reads to decide when to
   use this tool
3. **Input Schema** -- JSON Schema defining the parameters

Here is what a tool looks like from the protocol level:

```json
{
  "name": "get_interface_status",
  "description": "Get the operational status of a network interface on a device. Returns admin state, oper state, speed, and duplex. Use this when asked about interface health or link status.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "hostname": {
        "type": "string",
        "description": "Device hostname (e.g., 'switch-core-01')"
      },
      "interface": {
        "type": "string",
        "description": "Interface name (e.g., 'GigabitEthernet0/1')"
      }
    },
    "required": ["hostname", "interface"]
  }
}
```

The description is critical. The AI reads it to decide *when* to call this tool.
Write descriptions like you are explaining the tool to a new network engineer:
what it does, when to use it, what it returns.

## The Full Flow

Here is what happens when you ask an AI "Is interface Gi0/1 up on switch-core-01?"

```
1. You ask the question in Claude Desktop or the Streamlit chat UI (the MCP client)

2. The LLM sees it has a tool called "get_interface_status"
   with description: "Get the operational status of a network interface..."

3. The LLM decides this tool is relevant and calls it:
   {
     "tool": "get_interface_status",
     "arguments": {
       "hostname": "switch-core-01",
       "interface": "GigabitEthernet0/1"
     }
   }

4. The MCP server receives the call, runs your Python function

5. Your function connects to the device (or API) and gets the data

6. The server returns the result to the LLM:
   {
     "admin_status": "up",
     "oper_status": "up",
     "speed": "1Gbps",
     "duplex": "full"
   }

7. The LLM reads the result and responds in natural language:
   "Interface Gi0/1 on switch-core-01 is up/up, running at 1Gbps full duplex."
```

## Key Takeaways

- MCP is a protocol, not a library. It standardizes how AI models talk to tools.
- You build MCP servers that expose your network operations as tools.
- The AI discovers tools, reads their descriptions, and calls them when relevant.
- Think of it like SNMP for AI: you define what is queryable, the AI queries it.
- stdio transport is simplest for development. SSE/HTTP for production.
- Tool descriptions are as important as the code. The AI reads them to decide
  what to call.

## Next

In Lesson 02, you will build your first MCP server in Python.
