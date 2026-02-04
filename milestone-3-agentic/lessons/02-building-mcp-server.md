# Lesson 02: Building an MCP Server

## Goal

By the end of this lesson you will have a working MCP server written in Python
that exposes network tools an AI can call.

## The Python MCP SDK

The official Python SDK is `mcp`. Install it:

```bash
pip install mcp
```

Or with `uv` (recommended):

```bash
uv add mcp
```

The SDK provides `FastMCP`, a high-level class that handles all protocol details.
You register tools as decorated async functions, and the SDK handles discovery,
schema generation, and transport.

## Minimal Server: Hello Network

Here is the smallest possible MCP server:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hello-network")


@mcp.tool()
async def ping(hostname: str) -> str:
    """Ping a network device and return reachability status."""
    # In a real server, you would actually ping the device.
    return f"{hostname} is reachable (mock)"


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

That is it. Save it as `server.py` and you have a working MCP server.

### What is happening:

1. `FastMCP("hello-network")` creates a server with the name "hello-network"
2. `@mcp.tool()` registers the function as an MCP tool
3. The function signature (`hostname: str`) becomes the input schema automatically
4. The docstring becomes the tool description the AI reads
5. `mcp.run(transport="stdio")` starts the server, listening on stdin/stdout

## Running the Server

### With Python directly:

```bash
python server.py
```

The server starts and waits for MCP messages on stdin. You will not see output --
it is waiting for a client to connect.

### With `uv`:

```bash
uv run server.py
```

### Connecting to a client:

You can connect your MCP server to **Claude Desktop** (see
`final-boss/docs/claude-desktop-setup.md`) or the **Streamlit chat UI** powered
by Ollama (see the Final Boss project). You can also test your server manually
with the MCP Inspector (see below).

## Defining Tools with Type Hints

The SDK uses your function's type hints to generate the JSON Schema
automatically. Python types map to JSON Schema types:

| Python Type | JSON Schema | Example |
|------------|-------------|---------|
| `str` | `string` | `hostname: str` |
| `int` | `integer` | `vlan_id: int` |
| `float` | `number` | `threshold: float` |
| `bool` | `boolean` | `include_down: bool` |
| `list[str]` | `array` of `string` | `interfaces: list[str]` |
| `Optional[str]` | `string` or `null` | `description: Optional[str]` |

### Default Values

Parameters with defaults become optional in the schema:

```python
@mcp.tool()
async def list_interfaces(
    hostname: str,
    include_down: bool = False,
    name_filter: str | None = None,
) -> str:
    """List interfaces on a device.

    Args:
        hostname: Device hostname to query.
        include_down: If True, include administratively down interfaces.
        name_filter: Only return interfaces matching this substring.
    """
    # hostname is required, the rest are optional
    ...
```

## Using Pydantic Models for Complex Inputs

For tools with many parameters or nested data, use Pydantic models:

```python
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("network-tools")


class InterfaceQuery(BaseModel):
    """Query parameters for interface lookup."""

    hostname: str = Field(description="Device hostname")
    interface: str = Field(description="Interface name, e.g. 'GigabitEthernet0/1'")
    include_counters: bool = Field(
        default=False, description="Include traffic counters"
    )


@mcp.tool()
async def get_interface(query: InterfaceQuery) -> str:
    """Get detailed interface information from a network device."""
    return f"Interface {query.interface} on {query.hostname}: up/up"
```

Pydantic gives you:
- Field descriptions that appear in the schema (the AI reads these)
- Automatic validation (bad input is rejected before your code runs)
- Default values and optional fields
- Complex nested types

## Returning Results

Tools return strings. For structured data, return JSON:

```python
import json


@mcp.tool()
async def get_device_info(hostname: str) -> str:
    """Get basic information about a network device."""
    info = {
        "hostname": hostname,
        "model": "Cisco Catalyst 9300",
        "os_version": "17.09.04a",
        "serial": "FCW2245L0AB",
        "uptime_days": 142,
    }
    return json.dumps(info, indent=2)
```

The AI model can read both plain text and JSON. JSON is better when you want the
AI to parse specific fields or compare values across multiple calls.

## Error Handling

If your tool encounters an error, raise an exception or return an error message.
The SDK will relay it to the client:

```python
@mcp.tool()
async def get_device(hostname: str) -> str:
    """Look up a device by hostname."""
    devices = {"router-01": "10.0.0.1", "switch-01": "10.0.0.2"}

    if hostname not in devices:
        raise ValueError(f"Device '{hostname}' not found in inventory")

    return json.dumps({"hostname": hostname, "mgmt_ip": devices[hostname]})
```

Best practice: Return descriptive error messages. The AI reads them and can
explain the problem to the user or try a different approach.

## Project Structure

For a real MCP server, organize as a proper Python project:

```
my-network-mcp/
  pyproject.toml
  server.py
```

The `pyproject.toml`:

```toml
[project]
name = "my-network-mcp"
version = "0.1.0"
description = "MCP server for network operations"
requires-python = ">=3.11"
dependencies = [
    "mcp",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Testing Your Server

### Quick smoke test with Python:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"capabilities":{},"clientInfo":{"name":"test"},"protocolVersion":"2024-11-05"}}' | python server.py
```

If it returns a JSON response with server capabilities, your server works.

### With the MCP Inspector:

The MCP project provides an inspector tool for interactive testing:

```bash
npx @modelcontextprotocol/inspector python server.py
```

This opens a web UI where you can see your tools and call them manually.

## Complete Example: Multi-Tool Server

Here is a server with multiple tools for a network operations use case:

```python
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("network-ops")

# Mock device database
DEVICES = {
    "router-core-01": {
        "model": "Cisco ISR 4451",
        "mgmt_ip": "10.0.0.1",
        "os": "IOS-XE 17.09.04",
        "site": "dc-east",
    },
    "switch-access-01": {
        "model": "Cisco C9300-48P",
        "mgmt_ip": "10.0.1.1",
        "os": "IOS-XE 17.09.04",
        "site": "dc-east",
    },
}


@mcp.tool()
async def list_devices(site: str | None = None) -> str:
    """List all network devices in the inventory.

    Args:
        site: Optional site filter. Only return devices at this site.
    """
    results = {}
    for name, info in DEVICES.items():
        if site is None or info["site"] == site:
            results[name] = info
    return json.dumps(results, indent=2)


@mcp.tool()
async def get_device_info(hostname: str) -> str:
    """Get detailed information about a specific network device.

    Use this when asked about a particular device's model, IP, software,
    or site location.
    """
    if hostname not in DEVICES:
        raise ValueError(
            f"Device '{hostname}' not found. "
            f"Available: {', '.join(DEVICES.keys())}"
        )
    return json.dumps(DEVICES[hostname], indent=2)


@mcp.tool()
async def get_interface_status(hostname: str, interface: str) -> str:
    """Get the operational status of an interface on a network device.

    Returns admin state, operational state, speed, and duplex setting.
    Use this when asked about link status or interface health.
    """
    if hostname not in DEVICES:
        raise ValueError(f"Device '{hostname}' not found")

    status = {
        "hostname": hostname,
        "interface": interface,
        "admin_status": "up",
        "oper_status": "up",
        "speed": "1Gbps",
        "duplex": "full",
        "mtu": 1500,
        "description": f"Uplink from {hostname}",
    }
    return json.dumps(status, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## Key Takeaways

- `FastMCP` handles all protocol complexity. You just write functions.
- Type hints become the input schema. Docstrings become the tool description.
- Use Pydantic `Field(description=...)` when you need richer schema metadata.
- Return JSON strings for structured data.
- Raise exceptions with descriptive messages for error cases.
- Test with the MCP Inspector before connecting to Claude Desktop or the Streamlit UI.

## Next

In Lesson 03, you will learn why every write operation needs human approval --
the Human-in-the-Loop pattern.
