#!/usr/bin/env python3
"""
seed_netbox.py — Populate NetBox with lab data via the REST API.

This script creates all the foundational objects the network-automation lab
expects to find in NetBox:

  * Site, manufacturer, device type, device roles
  * Three cEOS switches with management + loopback IPs
  * A "server" prefix (10.0.1.0/24) containing a mix of:
      - IPs that ARE live on the switches  (via static ARP entries)
      - IPs that are NOT live              (intentional "stale" entries)
  * Point-to-point link prefixes and IPs

The deliberately stale IPs (10.0.1.50-52, 10.0.1.100-101) are the ones
the "Final Boss" automation agent should discover as unreachable.

Usage
-----
    # With defaults (http://localhost:8000, built-in lab token):
    python seed_netbox.py

    # With overrides:
    NETBOX_URL=http://netbox:8080 NETBOX_TOKEN=mytoken python seed_netbox.py

Requirements
------------
    pip install httpx
"""

from __future__ import annotations

import os
import sys
from typing import Any

import httpx

# =============================================================================
# Configuration — override via environment variables
# =============================================================================
NETBOX_URL: str = os.getenv("NETBOX_URL", "http://localhost:8000")
NETBOX_TOKEN: str = os.getenv(
    "NETBOX_TOKEN", "0123456789abcdef0123456789abcdef01234567"
)

# Strip trailing slash for consistent URL construction.
NETBOX_URL = NETBOX_URL.rstrip("/")

# =============================================================================
# HTTP client (re-used across all requests)
# =============================================================================
client = httpx.Client(
    base_url=f"{NETBOX_URL}/api",
    headers={
        "Authorization": f"Token {NETBOX_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    },
    timeout=30.0,
)


# =============================================================================
# Helper utilities
# =============================================================================

def _log(msg: str) -> None:
    """Print a timestamped status line."""
    print(f"  -> {msg}")


def _get_or_create(
    endpoint: str,
    lookup_params: dict[str, Any],
    create_payload: dict[str, Any],
    label: str,
) -> dict[str, Any]:
    """
    Idempotent create: search first, create only if missing.

    Parameters
    ----------
    endpoint : str
        API path relative to /api  (e.g. "/dcim/sites/").
    lookup_params : dict
        Query-string params used to check existence.
    create_payload : dict
        Full JSON body sent on POST if the object doesn't exist.
    label : str
        Human-readable name for log messages.

    Returns
    -------
    dict
        The existing or newly-created object (JSON).
    """
    # --- Check if the object already exists ----------------------------------
    resp = client.get(endpoint, params=lookup_params)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if results:
        _log(f"EXISTS  {label}")
        return results[0]

    # --- Create it -----------------------------------------------------------
    resp = client.post(endpoint, json=create_payload)
    if resp.status_code in (200, 201):
        _log(f"CREATE  {label}")
        return resp.json()

    # Provide a useful error message and bail out.
    print(f"  !! FAILED to create {label}: {resp.status_code}", file=sys.stderr)
    print(f"     {resp.text}", file=sys.stderr)
    resp.raise_for_status()
    return {}  # unreachable, keeps mypy happy


def _get_or_create_ip(
    address: str,
    status: str = "active",
    description: str = "",
    assigned_object_type: str | None = None,
    assigned_object_id: int | None = None,
) -> dict[str, Any]:
    """
    Convenience wrapper for creating an IP address.

    NetBox expects CIDR notation for IP addresses (e.g. "10.0.1.10/24").
    """
    payload: dict[str, Any] = {
        "address": address,
        "status": status,
        "description": description,
    }
    if assigned_object_type and assigned_object_id:
        payload["assigned_object_type"] = assigned_object_type
        payload["assigned_object_id"] = assigned_object_id

    return _get_or_create(
        "/ipam/ip-addresses/",
        {"address": address},
        payload,
        f"IP {address}",
    )


# =============================================================================
# Seed functions — called in dependency order
# =============================================================================

def create_site() -> dict[str, Any]:
    """Create the lab site."""
    print("\n[1/8] Site")
    return _get_or_create(
        "/dcim/sites/",
        {"name": "Lab"},
        {"name": "Lab", "slug": "lab", "status": "active"},
        "Site 'Lab'",
    )


def create_manufacturer() -> dict[str, Any]:
    """Create the Arista manufacturer."""
    print("\n[2/8] Manufacturer")
    return _get_or_create(
        "/dcim/manufacturers/",
        {"name": "Arista"},
        {"name": "Arista", "slug": "arista"},
        "Manufacturer 'Arista'",
    )


def create_device_type(manufacturer_id: int) -> dict[str, Any]:
    """Create the cEOS device type under Arista."""
    print("\n[3/8] Device Type")
    return _get_or_create(
        "/dcim/device-types/",
        {"model": "cEOS"},
        {
            "model": "cEOS",
            "slug": "ceos",
            "manufacturer": manufacturer_id,
        },
        "Device Type 'cEOS'",
    )


def create_device_roles() -> dict[str, dict[str, Any]]:
    """Create 'switch' and 'router' device roles."""
    print("\n[4/8] Device Roles")
    roles = {}
    for name, color in [("switch", "0000ff"), ("router", "ff0000")]:
        roles[name] = _get_or_create(
            "/dcim/device-roles/",
            {"name": name},
            {"name": name, "slug": name, "color": color, "vm_role": False},
            f"Role '{name}'",
        )
    return roles


def create_devices(
    site_id: int,
    device_type_id: int,
    role_id: int,
) -> dict[str, dict[str, Any]]:
    """Create the three cEOS switches."""
    print("\n[5/8] Devices")
    devices: dict[str, dict[str, Any]] = {}
    for name in ("switch-01", "switch-02", "switch-03"):
        devices[name] = _get_or_create(
            "/dcim/devices/",
            {"name": name},
            {
                "name": name,
                "site": site_id,
                "device_type": device_type_id,
                "role": role_id,
                "status": "active",
            },
            f"Device '{name}'",
        )
    return devices


def create_prefixes() -> None:
    """
    Create IP prefixes for the lab.

    Prefixes
    --------
      172.20.20.0/24  — Management network
      10.0.0.0/32s    — Loopbacks (created as IPs, not prefixes)
      10.0.1.0/24     — Simulated server/host subnet
      10.0.12.0/30    — switch-01 <-> switch-02 p2p
      10.0.23.0/30    — switch-02 <-> switch-03 p2p
      10.0.13.0/30    — switch-01 <-> switch-03 p2p
    """
    print("\n[6/8] Prefixes")
    prefixes = [
        ("172.20.20.0/24", "Management network (lab-net)"),
        ("10.0.1.0/24", "Server / host subnet (mixed live + stale IPs)"),
        ("10.0.12.0/30", "P2P: switch-01 <-> switch-02"),
        ("10.0.23.0/30", "P2P: switch-02 <-> switch-03"),
        ("10.0.13.0/30", "P2P: switch-01 <-> switch-03"),
    ]
    for prefix, desc in prefixes:
        _get_or_create(
            "/ipam/prefixes/",
            {"prefix": prefix},
            {"prefix": prefix, "status": "active", "description": desc},
            f"Prefix {prefix}",
        )


def create_ip_addresses() -> None:
    """
    Create all lab IP addresses.

    The 10.0.1.0/24 subnet is deliberately split into two groups:

      LIVE IPs   — have matching static ARP entries on the switches.
                   The agent should confirm these as reachable.

      STALE IPs  — exist ONLY in NetBox.  No ARP entry, no host.
                   The agent should flag these as unreachable / stale.
    """
    print("\n[7/8] IP Addresses")

    # --- Management IPs ------------------------------------------------------
    _log("Management IPs...")
    _get_or_create_ip("172.20.20.11/24", description="switch-01 Management0")
    _get_or_create_ip("172.20.20.12/24", description="switch-02 Management0")
    _get_or_create_ip("172.20.20.13/24", description="switch-03 Management0")

    # --- Loopback IPs --------------------------------------------------------
    _log("Loopback IPs...")
    _get_or_create_ip("10.0.0.1/32", description="switch-01 Loopback0")
    _get_or_create_ip("10.0.0.2/32", description="switch-02 Loopback0")
    _get_or_create_ip("10.0.0.3/32", description="switch-03 Loopback0")

    # --- Point-to-point link IPs ---------------------------------------------
    _log("Point-to-point link IPs...")
    _get_or_create_ip("10.0.12.1/30", description="switch-01 eth1 (-> sw02)")
    _get_or_create_ip("10.0.12.2/30", description="switch-02 eth1 (-> sw01)")
    _get_or_create_ip("10.0.23.1/30", description="switch-02 eth2 (-> sw03)")
    _get_or_create_ip("10.0.23.2/30", description="switch-03 eth1 (-> sw02)")
    _get_or_create_ip("10.0.13.1/30", description="switch-01 eth2 (-> sw03)")
    _get_or_create_ip("10.0.13.2/30", description="switch-03 eth2 (-> sw01)")

    # --- Server subnet: LIVE IPs (have ARP entries on switches) --------------
    _log("Server subnet — LIVE IPs (will answer pings)...")
    # switch-01 ARP table
    _get_or_create_ip("10.0.1.10/24", description="Live host (switch-01 ARP)")
    _get_or_create_ip("10.0.1.11/24", description="Live host (switch-01 ARP)")
    _get_or_create_ip("10.0.1.12/24", description="Live host (switch-01 ARP)")
    # switch-02 ARP table
    _get_or_create_ip("10.0.1.20/24", description="Live host (switch-02 ARP)")
    _get_or_create_ip("10.0.1.21/24", description="Live host (switch-02 ARP)")
    # switch-03 ARP table
    _get_or_create_ip("10.0.1.30/24", description="Live host (switch-03 ARP)")

    # --- Server subnet: STALE IPs (exist ONLY in NetBox — no ARP entry) ------
    _log("Server subnet — STALE IPs (NetBox-only, no ARP on any switch)...")
    _get_or_create_ip("10.0.1.50/24", description="Stale — no matching ARP entry")
    _get_or_create_ip("10.0.1.51/24", description="Stale — no matching ARP entry")
    _get_or_create_ip("10.0.1.52/24", description="Stale — no matching ARP entry")
    _get_or_create_ip("10.0.1.100/24", description="Stale — no matching ARP entry")
    _get_or_create_ip("10.0.1.101/24", description="Stale — no matching ARP entry")


def assign_primary_ips(devices: dict[str, dict[str, Any]]) -> None:
    """
    Assign management IPs as the primary IP for each device.

    This allows NetBox to display the management address on the device
    detail page and makes the devices queryable by IP.
    """
    print("\n[8/8] Assigning primary IPs to devices")

    mgmt_map = {
        "switch-01": "172.20.20.11/24",
        "switch-02": "172.20.20.12/24",
        "switch-03": "172.20.20.13/24",
    }

    for device_name, mgmt_address in mgmt_map.items():
        device = devices[device_name]
        device_id = device["id"]

        # Look up the IP address object.
        resp = client.get("/ipam/ip-addresses/", params={"address": mgmt_address})
        resp.raise_for_status()
        results = resp.json().get("results", [])
        if not results:
            _log(f"SKIP    {device_name} — IP {mgmt_address} not found")
            continue

        ip_id = results[0]["id"]

        # Look up the Management0 interface on the device.
        intf_resp = client.get(
            "/dcim/interfaces/",
            params={"device_id": device_id, "name": "Management0"},
        )
        intf_resp.raise_for_status()
        intf_results = intf_resp.json().get("results", [])

        # If the interface exists, assign the IP to it.
        if intf_results:
            intf_id = intf_results[0]["id"]
            client.patch(
                f"/ipam/ip-addresses/{ip_id}/",
                json={
                    "assigned_object_type": "dcim.interface",
                    "assigned_object_id": intf_id,
                },
            )

        # Set the device's primary_ip4 field.
        patch_resp = client.patch(
            f"/dcim/devices/{device_id}/",
            json={"primary_ip4": ip_id},
        )
        if patch_resp.status_code == 200:
            _log(f"ASSIGN  {device_name} -> {mgmt_address}")
        else:
            _log(
                f"WARN    Could not assign primary IP for {device_name}: "
                f"{patch_resp.status_code}"
            )


# =============================================================================
# Main entry point
# =============================================================================

def main() -> None:
    """Run the full seed sequence."""
    print("=" * 60)
    print("  NetBox Lab Seeder")
    print(f"  Target : {NETBOX_URL}")
    print("=" * 60)

    # Verify connectivity before doing anything.
    try:
        health = client.get("/status/")
        health.raise_for_status()
        _log(f"NetBox is reachable (HTTP {health.status_code})")
    except httpx.HTTPError as exc:
        print(
            f"\n  !! Cannot reach NetBox at {NETBOX_URL}/api/status/\n"
            f"     {exc}\n"
            f"  Make sure NetBox is running and NETBOX_URL is correct.\n",
            file=sys.stderr,
        )
        sys.exit(1)

    # Seed in dependency order.
    site = create_site()
    manufacturer = create_manufacturer()
    device_type = create_device_type(manufacturer["id"])
    roles = create_device_roles()
    devices = create_devices(site["id"], device_type["id"], roles["switch"]["id"])
    create_prefixes()
    create_ip_addresses()
    assign_primary_ips(devices)

    print("\n" + "=" * 60)
    print("  Seeding complete!")
    print("=" * 60)
    print(
        f"\n  Open NetBox at {NETBOX_URL} and log in with admin / admin.\n"
        f"  The API token for scripts is: {NETBOX_TOKEN}\n"
    )


if __name__ == "__main__":
    main()
