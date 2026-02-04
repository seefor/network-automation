"""
Lab 01: Hello MCP - A minimal MCP server with mock network tools.

This server exposes two read-only tools that return mock device data.
It demonstrates the basic MCP server pattern: define tools with type hints
and docstrings, and the SDK handles the rest.

Run:
    uv run server.py

Test with MCP Inspector:
    npx @modelcontextprotocol/inspector uv run server.py
"""

import json

from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hello-network")

# ---------------------------------------------------------------------------
# Mock data -- in a real server, this would come from NAPALM, Netmiko, or an API.
# ---------------------------------------------------------------------------

DEVICES: dict[str, dict] = {
    "router-core-01": {
        "hostname": "router-core-01",
        "model": "Cisco ISR 4451-X",
        "os_version": "IOS-XE 17.09.04a",
        "serial_number": "FJC2327U0BV",
        "mgmt_ip": "10.0.0.1",
        "site": "dc-east",
        "role": "core-router",
        "uptime_days": 142,
    },
    "switch-access-01": {
        "hostname": "switch-access-01",
        "model": "Cisco Catalyst 9300-48P",
        "os_version": "IOS-XE 17.09.04a",
        "serial_number": "FCW2245L0AB",
        "mgmt_ip": "10.0.1.1",
        "site": "dc-east",
        "role": "access-switch",
        "uptime_days": 87,
    },
    "switch-access-02": {
        "hostname": "switch-access-02",
        "model": "Cisco Catalyst 9300-48P",
        "os_version": "IOS-XE 17.09.04a",
        "serial_number": "FCW2245L0CD",
        "mgmt_ip": "10.0.1.2",
        "site": "dc-west",
        "role": "access-switch",
        "uptime_days": 63,
    },
}

INTERFACES: dict[str, dict[str, dict]] = {
    "router-core-01": {
        "GigabitEthernet0/0/0": {
            "admin_status": "up",
            "oper_status": "up",
            "speed": "1Gbps",
            "duplex": "full",
            "mtu": 1500,
            "description": "Uplink to ISP-A",
            "ip_address": "203.0.113.1/30",
        },
        "GigabitEthernet0/0/1": {
            "admin_status": "up",
            "oper_status": "up",
            "speed": "1Gbps",
            "duplex": "full",
            "mtu": 9000,
            "description": "To switch-access-01",
            "ip_address": "10.0.0.1/30",
        },
        "GigabitEthernet0/0/2": {
            "admin_status": "up",
            "oper_status": "down",
            "speed": "1Gbps",
            "duplex": "full",
            "mtu": 1500,
            "description": "To switch-access-02 (DOWN)",
            "ip_address": "10.0.0.5/30",
        },
    },
    "switch-access-01": {
        "GigabitEthernet1/0/1": {
            "admin_status": "up",
            "oper_status": "up",
            "speed": "1Gbps",
            "duplex": "full",
            "mtu": 1500,
            "description": "Server-01 eth0",
            "vlan": 100,
        },
        "GigabitEthernet1/0/2": {
            "admin_status": "up",
            "oper_status": "up",
            "speed": "1Gbps",
            "duplex": "full",
            "mtu": 1500,
            "description": "Server-02 eth0",
            "vlan": 200,
        },
        "GigabitEthernet1/0/48": {
            "admin_status": "down",
            "oper_status": "down",
            "speed": "auto",
            "duplex": "auto",
            "mtu": 1500,
            "description": "UNUSED",
            "vlan": 999,
        },
    },
}


# ---------------------------------------------------------------------------
# Pydantic models for tool inputs
# ---------------------------------------------------------------------------


class DeviceInfoRequest(BaseModel):
    """Request parameters for device info lookup."""

    hostname: str = Field(
        description="The hostname of the device to look up (e.g., 'router-core-01')"
    )


class InterfaceStatusRequest(BaseModel):
    """Request parameters for interface status lookup."""

    hostname: str = Field(
        description="The hostname of the device (e.g., 'switch-access-01')"
    )
    interface: str = Field(
        description="The interface name (e.g., 'GigabitEthernet1/0/1')"
    )


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_device_info(hostname: str) -> str:
    """Get detailed information about a network device.

    Returns the device model, OS version, serial number, management IP,
    site location, role, and uptime. Use this when asked about a specific
    device's details or inventory information.
    """
    if hostname not in DEVICES:
        available = ", ".join(sorted(DEVICES.keys()))
        raise ValueError(
            f"Device '{hostname}' not found in inventory. "
            f"Available devices: {available}"
        )

    return json.dumps(DEVICES[hostname], indent=2)


@mcp.tool()
async def get_interface_status(hostname: str, interface: str) -> str:
    """Get the operational status of a specific interface on a network device.

    Returns admin state, operational state, speed, duplex, MTU, and
    description. Use this when asked about link status, interface health,
    or port configuration.
    """
    if hostname not in INTERFACES:
        available = ", ".join(sorted(INTERFACES.keys()))
        raise ValueError(
            f"Device '{hostname}' not found. Available devices: {available}"
        )

    device_interfaces = INTERFACES[hostname]
    if interface not in device_interfaces:
        available = ", ".join(sorted(device_interfaces.keys()))
        raise ValueError(
            f"Interface '{interface}' not found on {hostname}. "
            f"Available interfaces: {available}"
        )

    result = {"hostname": hostname, "interface": interface}
    result.update(device_interfaces[interface])
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
