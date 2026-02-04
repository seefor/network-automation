#!/usr/bin/env python3
"""
Lab 02: Python Requests + NetBox
=================================

In this lab you will use the Python `requests` library to perform CRUD
operations against the NetBox REST API.

Prerequisites:
    - NetBox running at http://localhost:8000
    - pip install requests python-dotenv
    - A .env file in this directory with:
        NETBOX_URL=http://localhost:8000
        NETBOX_TOKEN=your-api-token-here

Instructions:
    - Work through each exercise in order.
    - Replace the TODO comments with your code.
    - Run the script: python lab02_python_requests.py
    - Each exercise prints its results. Verify against NetBox UI.
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


def main() -> None:
    session: requests.Session = create_session()
    print("=== Lab 02: Python Requests + NetBox ===\n")

    # -------------------------------------------------------------------------
    # Exercise 1: GET all sites
    # -------------------------------------------------------------------------
    # Fetch all sites from NetBox and print each site's name and slug.
    #
    # Endpoint: GET /api/dcim/sites/
    # Access the results with: response.json()["results"]
    #
    # Expected output format:
    #   Site: DC-East (slug: dc-east)
    #   Site: DC-West (slug: dc-west)
    # -------------------------------------------------------------------------
    print("--- Exercise 1: GET all sites ---")
    # TODO: Make a GET request to the sites endpoint
    # TODO: Check response.ok or call response.raise_for_status()
    # TODO: Loop through results and print each site's name and slug
    print()

    # -------------------------------------------------------------------------
    # Exercise 2: GET all devices with filtering
    # -------------------------------------------------------------------------
    # Fetch devices from NetBox. Use the params= argument to filter by status.
    #
    # Endpoint: GET /api/dcim/devices/
    # Query parameter: status=active
    #
    # Print each device's name, status, and site name.
    # Access nested site name: device["site"]["name"]
    #
    # Expected output format:
    #   spine-01 | active | DC-East
    #   leaf-01  | active | DC-East
    # -------------------------------------------------------------------------
    print("--- Exercise 2: GET active devices ---")
    # TODO: Make a GET request with params={"status": "active"}
    # TODO: Loop through results and print name, status, and site name
    print()

    # -------------------------------------------------------------------------
    # Exercise 3: GET all IP addresses
    # -------------------------------------------------------------------------
    # Fetch all IP addresses and print each one with its assigned interface
    # (if any).
    #
    # Endpoint: GET /api/ipam/ip-addresses/
    #
    # The assigned_object_id field will be set if the IP is assigned.
    # Print format:
    #   10.0.0.1/24 - assigned to: GigabitEthernet0/0
    #   10.0.0.2/24 - unassigned
    # -------------------------------------------------------------------------
    print("--- Exercise 3: GET all IP addresses ---")
    # TODO: Make a GET request to the ip-addresses endpoint
    # TODO: Loop through results
    # TODO: Check if "assigned_object" is not None; if so, print its display name
    # TODO: Otherwise, print "unassigned"
    print()

    # -------------------------------------------------------------------------
    # Exercise 4: POST - Create a new device
    # -------------------------------------------------------------------------
    # Create a new device called "lab-test-device" in NetBox.
    #
    # Endpoint: POST /api/dcim/devices/
    #
    # Required fields (use IDs from your NetBox instance):
    #   name: "lab-test-device"
    #   role: <device_role_id>       (integer)
    #   device_type: <device_type_id> (integer)
    #   site: <site_id>              (integer)
    #   status: "active"
    #
    # Use json= (not data=) to send the payload.
    # Store the created device's ID for later exercises.
    #
    # Hint: if you don't know the IDs, first GET /api/dcim/device-roles/,
    #       /api/dcim/device-types/, and /api/dcim/sites/ to find them.
    # -------------------------------------------------------------------------
    print("--- Exercise 4: POST a new device ---")
    created_device_id: int | None = None
    # TODO: Define the payload dict with name, role, device_type, site, status
    # TODO: Make a POST request with json=payload
    # TODO: Check response.ok; if successful, store the ID and print it
    # TODO: If failed, print the error: response.status_code and response.json()
    print()

    # -------------------------------------------------------------------------
    # Exercise 5: PATCH - Update the device
    # -------------------------------------------------------------------------
    # Update the device you just created. Change its status to "planned"
    # and add a comment.
    #
    # Endpoint: PATCH /api/dcim/devices/<id>/
    # Payload: {"status": "planned", "comments": "Updated via API lab"}
    #
    # Use the created_device_id from Exercise 4.
    # -------------------------------------------------------------------------
    print("--- Exercise 5: PATCH the device ---")
    if created_device_id is None:
        print("SKIP: No device was created in Exercise 4.")
    else:
        pass
        # TODO: Define the updates dict
        # TODO: Make a PATCH request to the device detail endpoint
        # TODO: Print the updated status from the response
    print()

    # -------------------------------------------------------------------------
    # Exercise 6: POST - Create an IP address and assign it
    # -------------------------------------------------------------------------
    # Create a new IP address in NetBox.
    #
    # Endpoint: POST /api/ipam/ip-addresses/
    # Payload:
    #   address: "10.255.255.1/32"
    #   status: "active"
    #   description: "Loopback for lab-test-device"
    #
    # Store the created IP's ID for the DELETE exercise.
    # -------------------------------------------------------------------------
    print("--- Exercise 6: POST a new IP address ---")
    created_ip_id: int | None = None
    # TODO: Define the payload dict
    # TODO: Make a POST request with json=payload
    # TODO: Store the created IP's ID and print confirmation
    print()

    # -------------------------------------------------------------------------
    # Exercise 7: DELETE - Clean up the IP address
    # -------------------------------------------------------------------------
    # Delete the IP address created in Exercise 6.
    #
    # Endpoint: DELETE /api/ipam/ip-addresses/<id>/
    # Expected: 204 No Content
    # -------------------------------------------------------------------------
    print("--- Exercise 7: DELETE the IP address ---")
    if created_ip_id is None:
        print("SKIP: No IP was created in Exercise 6.")
    else:
        pass
        # TODO: Make a DELETE request to the IP address detail endpoint
        # TODO: Check that response.status_code == 204
        # TODO: Print confirmation
    print()

    # -------------------------------------------------------------------------
    # Exercise 8: DELETE - Clean up the device
    # -------------------------------------------------------------------------
    # Delete the device created in Exercise 4.
    #
    # Endpoint: DELETE /api/dcim/devices/<id>/
    # Expected: 204 No Content
    # -------------------------------------------------------------------------
    print("--- Exercise 8: DELETE the device ---")
    if created_device_id is None:
        print("SKIP: No device was created in Exercise 4.")
    else:
        pass
        # TODO: Make a DELETE request to the device detail endpoint
        # TODO: Check that response.status_code == 204
        # TODO: Print confirmation
    print()

    print("=== Lab 02 Complete ===")


if __name__ == "__main__":
    main()
