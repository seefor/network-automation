#!/usr/bin/env python3
"""
Lab 02: Python Requests + NetBox -- SOLUTION
=============================================
"""

import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

NETBOX_URL: str = os.getenv("NETBOX_URL", "http://localhost:8000")
NETBOX_TOKEN: str = os.getenv("NETBOX_TOKEN", "")

if not NETBOX_TOKEN:
    print("ERROR: NETBOX_TOKEN not set. Add it to your .env file.")
    sys.exit(1)


def create_session() -> requests.Session:
    """Create a requests session with NetBox auth headers."""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Token {NETBOX_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    })
    return session


def get_first_id(session: requests.Session, endpoint: str) -> int | None:
    """Helper: fetch the first object's ID from a list endpoint."""
    response = session.get(f"{NETBOX_URL}{endpoint}")
    response.raise_for_status()
    results: list[dict] = response.json().get("results", [])
    if results:
        return results[0]["id"]
    return None


def main() -> None:
    session: requests.Session = create_session()
    print("=== Lab 02: Python Requests + NetBox (Solution) ===\n")

    # -------------------------------------------------------------------------
    # Exercise 1: GET all sites
    # -------------------------------------------------------------------------
    print("--- Exercise 1: GET all sites ---")
    response = session.get(f"{NETBOX_URL}/api/dcim/sites/")
    response.raise_for_status()
    sites: list[dict] = response.json()["results"]
    for site in sites:
        print(f"  Site: {site['name']} (slug: {site['slug']})")
    if not sites:
        print("  No sites found. Create one in the NetBox UI first.")
    print()

    # -------------------------------------------------------------------------
    # Exercise 2: GET active devices
    # -------------------------------------------------------------------------
    print("--- Exercise 2: GET active devices ---")
    response = session.get(
        f"{NETBOX_URL}/api/dcim/devices/",
        params={"status": "active"},
    )
    response.raise_for_status()
    devices: list[dict] = response.json()["results"]
    for device in devices:
        site_name: str = device["site"]["name"] if device.get("site") else "N/A"
        status: str = device["status"]["value"] if isinstance(device["status"], dict) else str(device["status"])
        print(f"  {device['name']:20s} | {status:10s} | {site_name}")
    if not devices:
        print("  No active devices found.")
    print()

    # -------------------------------------------------------------------------
    # Exercise 3: GET all IP addresses
    # -------------------------------------------------------------------------
    print("--- Exercise 3: GET all IP addresses ---")
    response = session.get(f"{NETBOX_URL}/api/ipam/ip-addresses/")
    response.raise_for_status()
    ips: list[dict] = response.json()["results"]
    for ip in ips:
        address: str = ip["address"]
        if ip.get("assigned_object"):
            iface: str = ip["assigned_object"].get("display", "unknown")
            print(f"  {address:20s} - assigned to: {iface}")
        else:
            print(f"  {address:20s} - unassigned")
    if not ips:
        print("  No IP addresses found.")
    print()

    # -------------------------------------------------------------------------
    # Exercise 4: POST a new device
    # -------------------------------------------------------------------------
    print("--- Exercise 4: POST a new device ---")
    created_device_id: int | None = None

    # Look up IDs for required foreign keys
    role_id: int | None = get_first_id(session, "/api/dcim/device-roles/")
    dtype_id: int | None = get_first_id(session, "/api/dcim/device-types/")
    site_id: int | None = get_first_id(session, "/api/dcim/sites/")

    if not all([role_id, dtype_id, site_id]):
        print("  SKIP: Need at least one device role, device type, and site in NetBox.")
    else:
        payload: dict = {
            "name": "lab-test-device",
            "role": role_id,
            "device_type": dtype_id,
            "site": site_id,
            "status": "active",
        }
        response = session.post(f"{NETBOX_URL}/api/dcim/devices/", json=payload)
        if response.ok:
            created: dict = response.json()
            created_device_id = created["id"]
            print(f"  Created device: {created['name']} (ID: {created_device_id})")
        else:
            print(f"  Error {response.status_code}: {response.json()}")
    print()

    # -------------------------------------------------------------------------
    # Exercise 5: PATCH the device
    # -------------------------------------------------------------------------
    print("--- Exercise 5: PATCH the device ---")
    if created_device_id is None:
        print("  SKIP: No device was created in Exercise 4.")
    else:
        updates: dict = {
            "status": "planned",
            "comments": "Updated via API lab",
        }
        response = session.patch(
            f"{NETBOX_URL}/api/dcim/devices/{created_device_id}/",
            json=updates,
        )
        response.raise_for_status()
        updated: dict = response.json()
        status_val: str = updated["status"]["value"] if isinstance(updated["status"], dict) else str(updated["status"])
        print(f"  Device {updated['name']} status updated to: {status_val}")
        print(f"  Comments: {updated.get('comments', '')}")
    print()

    # -------------------------------------------------------------------------
    # Exercise 6: POST a new IP address
    # -------------------------------------------------------------------------
    print("--- Exercise 6: POST a new IP address ---")
    created_ip_id: int | None = None

    ip_payload: dict = {
        "address": "10.255.255.1/32",
        "status": "active",
        "description": "Loopback for lab-test-device",
    }
    response = session.post(f"{NETBOX_URL}/api/ipam/ip-addresses/", json=ip_payload)
    if response.ok:
        created_ip: dict = response.json()
        created_ip_id = created_ip["id"]
        print(f"  Created IP: {created_ip['address']} (ID: {created_ip_id})")
    else:
        print(f"  Error {response.status_code}: {response.json()}")
    print()

    # -------------------------------------------------------------------------
    # Exercise 7: DELETE the IP address
    # -------------------------------------------------------------------------
    print("--- Exercise 7: DELETE the IP address ---")
    if created_ip_id is None:
        print("  SKIP: No IP was created in Exercise 6.")
    else:
        response = session.delete(f"{NETBOX_URL}/api/ipam/ip-addresses/{created_ip_id}/")
        if response.status_code == 204:
            print(f"  Deleted IP address ID {created_ip_id} (HTTP 204)")
        else:
            print(f"  Unexpected status: {response.status_code}")
    print()

    # -------------------------------------------------------------------------
    # Exercise 8: DELETE the device
    # -------------------------------------------------------------------------
    print("--- Exercise 8: DELETE the device ---")
    if created_device_id is None:
        print("  SKIP: No device was created in Exercise 4.")
    else:
        response = session.delete(f"{NETBOX_URL}/api/dcim/devices/{created_device_id}/")
        if response.status_code == 204:
            print(f"  Deleted device ID {created_device_id} (HTTP 204)")
        else:
            print(f"  Unexpected status: {response.status_code}")
    print()

    print("=== Lab 02 Complete ===")


if __name__ == "__main__":
    main()
