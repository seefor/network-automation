"""
Lab 02: NetBox MCP - An MCP server connected to a real NetBox instance.

This server exposes read-only tools for querying NetBox device inventory
and IPAM data. It uses httpx for async HTTP calls to the NetBox REST API.

Configuration (environment variables):
    NETBOX_URL   - Base URL of your NetBox instance (e.g., https://netbox.example.com)
    NETBOX_TOKEN - API token for authentication

Run:
    NETBOX_URL=https://netbox.example.com NETBOX_TOKEN=abc123 uv run server.py

Test with MCP Inspector:
    NETBOX_URL=https://netbox.example.com NETBOX_TOKEN=abc123 \
        npx @modelcontextprotocol/inspector uv run server.py
"""

import json
import os
from typing import Any

import httpx

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("netbox-mcp")

# ---------------------------------------------------------------------------
# NetBox API client
# ---------------------------------------------------------------------------

NETBOX_URL = os.environ.get("NETBOX_URL", "")
NETBOX_TOKEN = os.environ.get("NETBOX_TOKEN", "")


def _get_headers() -> dict[str, str]:
    """Build HTTP headers for NetBox API requests."""
    if not NETBOX_TOKEN:
        raise RuntimeError(
            "NETBOX_TOKEN environment variable is not set. "
            "Set it to your NetBox API token."
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
            "Set it to your NetBox instance URL (e.g., https://netbox.example.com)."
        )
    return NETBOX_URL.rstrip("/")


async def _netbox_get(path: str, params: dict[str, Any] | None = None) -> dict:
    """Make a GET request to the NetBox API.

    Args:
        path: API path (e.g., '/api/dcim/devices/')
        params: Optional query parameters

    Returns:
        Parsed JSON response

    Raises:
        RuntimeError: If the request fails
    """
    url = f"{_get_base_url()}{path}"

    async with httpx.AsyncClient(timeout=30.0, verify=True) as client:
        try:
            response = await client.get(url, headers=_get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"NetBox API error: {exc.response.status_code} - "
                f"{exc.response.text[:500]}"
            ) from exc
        except httpx.ConnectError as exc:
            raise RuntimeError(
                f"Cannot connect to NetBox at {_get_base_url()}. "
                f"Check NETBOX_URL is correct and the server is reachable. "
                f"Error: {exc}"
            ) from exc


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
    and primary IP. Use this to get an overview of what devices exist
    or to filter by site/role.

    Args:
        site: Filter by site slug (e.g., 'dc-east'). Optional.
        role: Filter by device role slug (e.g., 'core-router'). Optional.
        limit: Maximum number of results to return. Default 50.
    """
    params: dict[str, Any] = {"limit": limit}
    if site:
        params["site"] = site
    if role:
        params["role"] = role

    data = await _netbox_get("/api/dcim/devices/", params=params)

    devices = []
    for device in data.get("results", []):
        primary_ip = None
        if device.get("primary_ip"):
            primary_ip = device["primary_ip"].get("address")

        devices.append({
            "id": device["id"],
            "hostname": device["name"],
            "model": device.get("device_type", {}).get("display", "Unknown"),
            "site": device.get("site", {}).get("name", "Unknown"),
            "role": device.get("role", {}).get("name", "Unknown"),
            "status": device.get("status", {}).get("label", "Unknown"),
            "primary_ip": primary_ip,
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

    Returns full device details including model, serial number, site,
    rack position, primary IP, and custom fields. Use this when asked
    about a particular device.

    Args:
        hostname: The exact hostname (name) of the device in NetBox.
    """
    data = await _netbox_get("/api/dcim/devices/", params={"name": hostname})

    results = data.get("results", [])
    if not results:
        raise ValueError(
            f"Device '{hostname}' not found in NetBox. "
            f"Check the hostname is spelled correctly."
        )

    device = results[0]

    primary_ip = None
    if device.get("primary_ip"):
        primary_ip = device["primary_ip"].get("address")

    info = {
        "id": device["id"],
        "hostname": device["name"],
        "model": device.get("device_type", {}).get("display", "Unknown"),
        "manufacturer": device.get("device_type", {}).get("manufacturer", {}).get(
            "name", "Unknown"
        ),
        "serial_number": device.get("serial", ""),
        "asset_tag": device.get("asset_tag"),
        "site": device.get("site", {}).get("name", "Unknown"),
        "rack": device.get("rack", {}).get("name") if device.get("rack") else None,
        "position": device.get("position"),
        "role": device.get("role", {}).get("name", "Unknown"),
        "status": device.get("status", {}).get("label", "Unknown"),
        "platform": device.get("platform", {}).get("name")
        if device.get("platform")
        else None,
        "primary_ip": primary_ip,
        "comments": device.get("comments", ""),
        "tags": [tag["name"] for tag in device.get("tags", [])],
    }
    return json.dumps(info, indent=2)


@mcp.tool()
async def list_ip_addresses(prefix: str | None = None, limit: int = 50) -> str:
    """List IP addresses from NetBox IPAM.

    Returns IP addresses with their assignment status, DNS name, and
    assigned interface. Use this to see what IPs exist in a prefix or
    to find a specific IP assignment.

    Args:
        prefix: Filter by parent prefix in CIDR notation (e.g., '10.0.0.0/24').
                Optional -- returns all IPs if not specified.
        limit: Maximum number of results. Default 50.
    """
    params: dict[str, Any] = {"limit": limit}
    if prefix:
        params["parent"] = prefix

    data = await _netbox_get("/api/ipam/ip-addresses/", params=params)

    addresses = []
    for ip in data.get("results", []):
        assigned_to = None
        if ip.get("assigned_object"):
            obj = ip["assigned_object"]
            device_name = obj.get("device", {}).get("name", "")
            iface_name = obj.get("name", "")
            if device_name and iface_name:
                assigned_to = f"{device_name} - {iface_name}"

        addresses.append({
            "address": ip["address"],
            "status": ip.get("status", {}).get("label", "Unknown"),
            "dns_name": ip.get("dns_name", ""),
            "description": ip.get("description", ""),
            "assigned_to": assigned_to,
            "tenant": ip.get("tenant", {}).get("name") if ip.get("tenant") else None,
        })

    result = {
        "count": data.get("count", 0),
        "returned": len(addresses),
        "addresses": addresses,
    }
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_prefix_utilization(prefix: str) -> str:
    """Get utilization statistics for a specific IP prefix.

    Returns the prefix size, how many IPs are used, percentage utilized,
    and available capacity. Use this to check if a subnet is running
    out of addresses or to plan capacity.

    Args:
        prefix: The prefix in CIDR notation (e.g., '10.0.0.0/24').
    """
    data = await _netbox_get("/api/ipam/prefixes/", params={"prefix": prefix})

    results = data.get("results", [])
    if not results:
        raise ValueError(
            f"Prefix '{prefix}' not found in NetBox. "
            f"Check the prefix is correct and exists in IPAM."
        )

    pfx = results[0]
    prefix_id = pfx["id"]

    # Fetch the available IPs count from the prefix detail
    detail = await _netbox_get(f"/api/ipam/prefixes/{prefix_id}/available-ips/")

    # Calculate utilization from child IP count
    child_ips = await _netbox_get(
        "/api/ipam/ip-addresses/", params={"parent": prefix, "limit": 1}
    )
    total_ips_used = child_ips.get("count", 0)

    # Parse CIDR to estimate total size
    cidr = int(prefix.split("/")[1])
    if cidr <= 30:
        total_addresses = (2 ** (32 - cidr)) - 2  # subtract network + broadcast
    else:
        total_addresses = 2 ** (32 - cidr)

    utilization_pct = (
        round((total_ips_used / total_addresses) * 100, 1)
        if total_addresses > 0
        else 0
    )

    info = {
        "prefix": pfx["prefix"],
        "description": pfx.get("description", ""),
        "site": pfx.get("site", {}).get("name") if pfx.get("site") else None,
        "vlan": pfx.get("vlan", {}).get("display") if pfx.get("vlan") else None,
        "status": pfx.get("status", {}).get("label", "Unknown"),
        "tenant": pfx.get("tenant", {}).get("name") if pfx.get("tenant") else None,
        "total_addresses": total_addresses,
        "ips_assigned": total_ips_used,
        "utilization_percent": utilization_pct,
        "available": total_addresses - total_ips_used,
    }
    return json.dumps(info, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
