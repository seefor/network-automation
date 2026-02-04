"""
Solution: Lab 02 - NetBox MCP

An MCP server that connects to a real NetBox instance, exposing read-only
tools for device inventory and IPAM queries.

Tools:
    list_devices          - List devices with optional site/role filters
    get_device            - Get full details for a specific device by hostname
    list_ip_addresses     - List IP addresses, optionally filtered by prefix
    get_prefix_utilization - Get utilization stats for a specific prefix

Configuration (environment variables):
    NETBOX_URL   - Base URL of your NetBox instance (e.g., https://netbox.example.com)
    NETBOX_TOKEN - API token for authentication

Run:
    NETBOX_URL=https://netbox.example.com NETBOX_TOKEN=abc123 uv run server.py

Test with MCP Inspector:
    NETBOX_URL=https://netbox.example.com NETBOX_TOKEN=abc123 \
        npx @modelcontextprotocol/inspector uv run server.py

Connect to Claude Desktop (add to claude_desktop_config.json):
    {
      "mcpServers": {
        "netbox": {
          "command": "uv",
          "args": ["run", "/absolute/path/to/server.py"],
          "env": {
            "NETBOX_URL": "https://netbox.example.com",
            "NETBOX_TOKEN": "your-token-here"
          }
        }
      }
    }
"""

import json
import os
from typing import Any

import httpx

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("netbox-mcp")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

NETBOX_URL = os.environ.get("NETBOX_URL", "")
NETBOX_TOKEN = os.environ.get("NETBOX_TOKEN", "")


# ---------------------------------------------------------------------------
# NetBox API client
# ---------------------------------------------------------------------------


def _get_headers() -> dict[str, str]:
    """Build HTTP headers for NetBox API requests."""
    if not NETBOX_TOKEN:
        raise RuntimeError(
            "NETBOX_TOKEN environment variable is not set. "
            "Export it before running: export NETBOX_TOKEN='your-token'"
        )
    return {
        "Authorization": f"Token {NETBOX_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _get_base_url() -> str:
    """Get and validate the NetBox base URL."""
    if not NETBOX_URL:
        raise RuntimeError(
            "NETBOX_URL environment variable is not set. "
            "Export it before running: export NETBOX_URL='https://netbox.example.com'"
        )
    return NETBOX_URL.rstrip("/")


async def _netbox_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """Make a GET request to the NetBox API.

    Args:
        path: API path starting with / (e.g., '/api/dcim/devices/')
        params: Optional query parameters

    Returns:
        Parsed JSON response (dict or list depending on endpoint)

    Raises:
        RuntimeError: If the request fails or NetBox is unreachable
    """
    url = f"{_get_base_url()}{path}"

    async with httpx.AsyncClient(timeout=30.0, verify=True) as client:
        try:
            response = await client.get(url, headers=_get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            body = exc.response.text[:500]
            if status == 401:
                raise RuntimeError(
                    "NetBox authentication failed (401). "
                    "Check your NETBOX_TOKEN is valid."
                ) from exc
            elif status == 403:
                raise RuntimeError(
                    "NetBox permission denied (403). "
                    "Your token may not have access to this endpoint."
                ) from exc
            elif status == 404:
                raise RuntimeError(
                    f"NetBox endpoint not found (404): {path}. "
                    f"Check your NETBOX_URL and API path."
                ) from exc
            else:
                raise RuntimeError(
                    f"NetBox API error: {status} - {body}"
                ) from exc
        except httpx.ConnectError as exc:
            raise RuntimeError(
                f"Cannot connect to NetBox at {_get_base_url()}. "
                f"Check that NETBOX_URL is correct and the server is reachable. "
                f"Error: {exc}"
            ) from exc
        except httpx.TimeoutException as exc:
            raise RuntimeError(
                f"Request to NetBox timed out after 30s. "
                f"The server may be slow or unreachable. URL: {url}"
            ) from exc


# ---------------------------------------------------------------------------
# Helper: safely extract nested fields from NetBox responses
# ---------------------------------------------------------------------------


def _safe_nested(obj: dict | None, *keys: str, default: Any = None) -> Any:
    """Safely traverse nested dicts. Returns default if any key is missing."""
    current = obj
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_devices(
    site: str | None = None,
    role: str | None = None,
    limit: int = 50,
) -> str:
    """List network devices from NetBox inventory.

    Returns a summary of devices including hostname, model, site, role,
    status, and primary IP. Use this to get an overview of the network
    inventory or to find devices at a specific site or with a specific role.

    Args:
        site: Filter by site slug (e.g., 'dc-east'). Optional.
        role: Filter by device role slug (e.g., 'core-router'). Optional.
        limit: Maximum number of results. Default 50.

    Example questions this answers:
    - "What devices do we have?"
    - "Show me all devices at dc-east"
    - "List all core routers"
    """
    params: dict[str, Any] = {"limit": limit}
    if site:
        params["site"] = site
    if role:
        params["role"] = role

    data = await _netbox_get("/api/dcim/devices/", params=params)

    devices = []
    for device in data.get("results", []):
        devices.append({
            "id": device["id"],
            "hostname": device["name"],
            "model": _safe_nested(device, "device_type", "display", default="Unknown"),
            "site": _safe_nested(device, "site", "name", default="Unknown"),
            "role": _safe_nested(device, "role", "name", default="Unknown"),
            "status": _safe_nested(device, "status", "label", default="Unknown"),
            "primary_ip": _safe_nested(device, "primary_ip", "address"),
        })

    result = {
        "count": data.get("count", 0),
        "returned": len(devices),
        "devices": devices,
    }
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_device(hostname: str) -> str:
    """Get detailed information about a specific device from NetBox.

    Returns full device details including model, manufacturer, serial number,
    site, rack, role, platform, primary IP, tags, and comments. Use this when
    asked about a particular device.

    Args:
        hostname: The exact hostname (name) of the device in NetBox.

    Example questions this answers:
    - "Tell me about router-core-01"
    - "What is the serial number of switch-access-01?"
    - "What rack is firewall-01 in?"
    """
    data = await _netbox_get("/api/dcim/devices/", params={"name": hostname})

    results = data.get("results", [])
    if not results:
        raise ValueError(
            f"Device '{hostname}' not found in NetBox. "
            f"Check the hostname is spelled correctly. "
            f"Use list_devices to see available hostnames."
        )

    device = results[0]

    info = {
        "id": device["id"],
        "hostname": device["name"],
        "model": _safe_nested(device, "device_type", "display", default="Unknown"),
        "manufacturer": _safe_nested(
            device, "device_type", "manufacturer", "name", default="Unknown"
        ),
        "serial_number": device.get("serial", ""),
        "asset_tag": device.get("asset_tag"),
        "site": _safe_nested(device, "site", "name", default="Unknown"),
        "rack": _safe_nested(device, "rack", "name"),
        "position": device.get("position"),
        "role": _safe_nested(device, "role", "name", default="Unknown"),
        "status": _safe_nested(device, "status", "label", default="Unknown"),
        "platform": _safe_nested(device, "platform", "name"),
        "primary_ip": _safe_nested(device, "primary_ip", "address"),
        "comments": device.get("comments", ""),
        "tags": [tag["name"] for tag in device.get("tags", [])],
        "url": device.get("url", ""),
    }
    return json.dumps(info, indent=2)


@mcp.tool()
async def list_ip_addresses(prefix: str | None = None, limit: int = 50) -> str:
    """List IP addresses from NetBox IPAM.

    Returns IP addresses with their assignment status, DNS name, description,
    and which device/interface they are assigned to. Use this to see what IPs
    are in use within a prefix or to find where an IP is assigned.

    Args:
        prefix: Filter by parent prefix in CIDR notation (e.g., '10.0.0.0/24').
                If omitted, returns IPs across all prefixes.
        limit: Maximum number of results. Default 50.

    Example questions this answers:
    - "What IPs are in the 10.0.0.0/24 subnet?"
    - "Show me all assigned IP addresses"
    - "Where is 10.0.1.5 assigned?"
    """
    params: dict[str, Any] = {"limit": limit}
    if prefix:
        params["parent"] = prefix

    data = await _netbox_get("/api/ipam/ip-addresses/", params=params)

    addresses = []
    for ip in data.get("results", []):
        # Determine what the IP is assigned to (device + interface)
        assigned_to = None
        assigned_obj = ip.get("assigned_object")
        if assigned_obj:
            device_name = _safe_nested(assigned_obj, "device", "name", default="")
            iface_name = assigned_obj.get("name", "")
            if device_name and iface_name:
                assigned_to = f"{device_name} - {iface_name}"
            elif device_name:
                assigned_to = device_name

        addresses.append({
            "address": ip["address"],
            "status": _safe_nested(ip, "status", "label", default="Unknown"),
            "dns_name": ip.get("dns_name", ""),
            "description": ip.get("description", ""),
            "assigned_to": assigned_to,
            "tenant": _safe_nested(ip, "tenant", "name"),
            "vrf": _safe_nested(ip, "vrf", "name"),
        })

    result = {
        "count": data.get("count", 0),
        "returned": len(addresses),
        "prefix_filter": prefix,
        "addresses": addresses,
    }
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_prefix_utilization(prefix: str) -> str:
    """Get utilization statistics for a specific IP prefix.

    Returns the prefix details, total address space, number of assigned IPs,
    utilization percentage, and remaining capacity. Use this to check if a
    subnet is running low on addresses or to plan capacity.

    Args:
        prefix: The prefix in CIDR notation (e.g., '10.0.0.0/24').

    Example questions this answers:
    - "How full is the 10.0.0.0/24 subnet?"
    - "Do we have room in the server VLAN?"
    - "What is the utilization of our management prefix?"
    """
    # Look up the prefix object
    data = await _netbox_get("/api/ipam/prefixes/", params={"prefix": prefix})

    results = data.get("results", [])
    if not results:
        raise ValueError(
            f"Prefix '{prefix}' not found in NetBox. "
            f"Check the prefix is in CIDR notation (e.g., '10.0.0.0/24') "
            f"and exists in IPAM."
        )

    pfx = results[0]
    prefix_id = pfx["id"]

    # Get count of child IP addresses assigned in this prefix
    child_ips = await _netbox_get(
        "/api/ipam/ip-addresses/",
        params={"parent": prefix, "limit": 1},
    )
    total_ips_used = child_ips.get("count", 0)

    # Calculate total usable addresses from CIDR
    cidr = int(prefix.split("/")[1])
    if cidr <= 30:
        # Standard subnets: subtract network and broadcast addresses
        total_addresses = (2 ** (32 - cidr)) - 2
    elif cidr == 31:
        # Point-to-point links (RFC 3021)
        total_addresses = 2
    else:
        # /32 host routes
        total_addresses = 1

    utilization_pct = (
        round((total_ips_used / total_addresses) * 100, 1)
        if total_addresses > 0
        else 0.0
    )

    info = {
        "prefix": pfx["prefix"],
        "description": pfx.get("description", ""),
        "site": _safe_nested(pfx, "site", "name"),
        "vlan": _safe_nested(pfx, "vlan", "display"),
        "role": _safe_nested(pfx, "role", "name"),
        "status": _safe_nested(pfx, "status", "label", default="Unknown"),
        "tenant": _safe_nested(pfx, "tenant", "name"),
        "is_pool": pfx.get("is_pool", False),
        "total_addresses": total_addresses,
        "ips_assigned": total_ips_used,
        "utilization_percent": utilization_pct,
        "addresses_available": total_addresses - total_ips_used,
    }
    return json.dumps(info, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
