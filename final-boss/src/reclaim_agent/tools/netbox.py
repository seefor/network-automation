"""
NetBox API Client
==================

This module provides an async HTTP client for interacting with the NetBox REST API.
NetBox is the Source of Truth (SoT) for IP address management (IPAM).

WHAT'S PROVIDED:
  - A working `get_version()` method (use as a reference for implementing the rest)

WHAT YOU NEED TO IMPLEMENT:
  - get_active_ips()  : Query IPs with status=active in a given prefix
  - deprecate_ip()    : Change an IP's status from active to deprecated
  - get_ip_details()  : Look up a single IP address by its address string

NetBox API documentation: https://demo.netbox.dev/static/docs/rest-api/overview/

Key concepts:
  - All API requests need the Authorization header: "Token <your-token>"
  - IP addresses live at: /api/ipam/ip-addresses/
  - Filter by prefix using: ?parent=<prefix>&status=active
  - Update status with a PATCH request to /api/ipam/ip-addresses/<id>/
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger("reclaim-agent.netbox")


class NetBoxClient:
    """Async HTTP client for the NetBox REST API.

    Usage:
        client = NetBoxClient(url="https://netbox.example.com", token="abc123")
        version = await client.get_version()
        ips = await client.get_active_ips("10.0.1.0/24")
    """

    def __init__(self, url: str, token: str) -> None:
        """Initialize the NetBox client.

        Args:
            url:   Base URL of the NetBox instance (e.g. "https://netbox.example.com").
            token: NetBox API token for authentication.
        """
        # Strip trailing slash to avoid double-slash in URL construction
        self.url = url.rstrip("/")
        self.token = token

        # Create a reusable async HTTP client with auth headers pre-configured
        self.client = httpx.AsyncClient(
            base_url=self.url,
            headers={
                "Authorization": f"Token {self.token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=30.0,
        )

    # -----------------------------------------------------------------------
    # EXAMPLE METHOD (fully implemented — use as reference)
    # -----------------------------------------------------------------------

    async def get_version(self) -> str:
        """Fetch the NetBox server version.

        This is the working example. Study how it:
          1. Makes an async GET request
          2. Raises on HTTP errors
          3. Parses the JSON response
          4. Returns a clean value

        Returns:
            Version string like "4.2.3".
        """
        response = await self.client.get("/api/status/")
        response.raise_for_status()
        data = response.json()
        return data.get("netbox-version", "unknown")

    # -----------------------------------------------------------------------
    # STUB: get_active_ips
    # -----------------------------------------------------------------------

    async def get_active_ips(self, prefix: str) -> list[dict[str, Any]]:
        """Query NetBox for all IP addresses with status 'active' in a prefix.

        Args:
            prefix: CIDR prefix to query, e.g. "10.0.1.0/24".

        Returns:
            A list of dicts, each containing at minimum:
              - "id": int              (NetBox object ID)
              - "address": str         (e.g. "10.0.1.5/24")
              - "status": dict         (e.g. {"value": "active", "label": "Active"})
              - "description": str     (IP description)
              - "dns_name": str        (reverse DNS name)

        Hints:
            - API endpoint: GET /api/ipam/ip-addresses/
            - Query params: parent=<prefix>, status=active
            - The response is paginated: check "next" field for more pages
            - Loop until "next" is None to get all results
            - Results are in the "results" key of the response JSON

        Example API call:
            GET /api/ipam/ip-addresses/?parent=10.0.1.0/24&status=active
        """
        # TODO: Implement this method
        # 1. Build the query parameters: {"parent": prefix, "status": "active"}
        # 2. Make a GET request to /api/ipam/ip-addresses/
        # 3. Handle pagination (loop while "next" is not None)
        # 4. Collect all results into a single list
        # 5. Return the list
        raise NotImplementedError("TODO: Implement get_active_ips")

    # -----------------------------------------------------------------------
    # STUB: deprecate_ip
    # -----------------------------------------------------------------------

    async def deprecate_ip(self, ip_id: int) -> dict[str, Any]:
        """Change an IP address status from 'active' to 'deprecated' in NetBox.

        Args:
            ip_id: The NetBox object ID of the IP address to deprecate.

        Returns:
            The updated IP address object dict from NetBox.

        Hints:
            - API endpoint: PATCH /api/ipam/ip-addresses/<id>/
            - Request body: {"status": "deprecated"}
            - Use self.client.patch() for the request
            - Check response.raise_for_status() for errors

        Example API call:
            PATCH /api/ipam/ip-addresses/42/
            Body: {"status": "deprecated"}
        """
        # TODO: Implement this method
        # 1. Make a PATCH request to /api/ipam/ip-addresses/{ip_id}/
        # 2. Send {"status": "deprecated"} as the JSON body
        # 3. Check for HTTP errors
        # 4. Return the response JSON (updated IP object)
        raise NotImplementedError("TODO: Implement deprecate_ip")

    # -----------------------------------------------------------------------
    # STUB: get_ip_details
    # -----------------------------------------------------------------------

    async def get_ip_details(self, address: str) -> dict[str, Any]:
        """Look up a single IP address in NetBox by its address string.

        Args:
            address: The IP address to look up, e.g. "10.0.1.15/24" or "10.0.1.15".

        Returns:
            The IP address object dict from NetBox, or an empty dict if not found.

        Hints:
            - API endpoint: GET /api/ipam/ip-addresses/?address=<address>
            - The response "results" list should have 0 or 1 entries
            - Return the first result if found, empty dict if not

        Example API call:
            GET /api/ipam/ip-addresses/?address=10.0.1.15
        """
        # TODO: Implement this method
        # 1. Make a GET request to /api/ipam/ip-addresses/ with address param
        # 2. Check if results list is non-empty
        # 3. Return the first result, or empty dict if not found
        raise NotImplementedError("TODO: Implement get_ip_details")

    # -----------------------------------------------------------------------
    # Cleanup
    # -----------------------------------------------------------------------

    async def close(self) -> None:
        """Close the underlying HTTP client. Call when done."""
        await self.client.aclose()
