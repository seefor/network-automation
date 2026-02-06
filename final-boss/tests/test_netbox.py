"""
Tests for the NetBox API Client
=================================

These tests verify your NetBoxClient implementation works correctly.

HOW TO RUN:
    uv run pytest tests/test_netbox.py -v

SETUP:
    These tests require a running NetBox instance. Make sure your .env file
    is configured with valid NETBOX_URL and NETBOX_TOKEN values.

    For local development, run `make lab-up` to start the lab NetBox instance.

WHAT TO TEST:
    - get_version()    : Should return a version string (already implemented)
    - get_active_ips() : Should return a list of active IP dicts for a prefix
    - deprecate_ip()   : Should change an IP's status to deprecated
"""

from __future__ import annotations

import pytest

from reclaim_agent.tools.netbox import NetBoxClient
from reclaim_agent.utils.config import Settings


# ---------------------------------------------------------------------------
# Fixtures — shared setup for all tests in this file
# ---------------------------------------------------------------------------


@pytest.fixture
def settings() -> Settings:
    """Load application settings from .env file."""
    return Settings()


@pytest.fixture
async def netbox_client(settings: Settings) -> NetBoxClient:
    """Create a NetBox client instance for testing.

    Yields the client and ensures cleanup after test completes.
    """
    client = NetBoxClient(url=settings.NETBOX_URL, token=settings.NETBOX_TOKEN)
    yield client
    await client.close()


# ---------------------------------------------------------------------------
# Test: get_version (working example — this test should pass immediately)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_version(netbox_client: NetBoxClient) -> None:
    """Test that get_version() returns a non-empty version string.

    This test verifies:
      - The NetBox client can connect to the server
      - The API token is valid
      - The response is parsed correctly
    """
    version = await netbox_client.get_version()

    assert version is not None, "Version should not be None"
    assert isinstance(version, str), "Version should be a string"
    assert version != "unknown", "Version should not be 'unknown' — check your connection"
    assert "." in version, f"Version should contain dots (got: {version})"


# ---------------------------------------------------------------------------
# Test: get_active_ips (TODO — implement after you build the method)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_active_ips(netbox_client: NetBoxClient) -> None:
    """Test that get_active_ips() returns allocated IPs for a prefix.

    TODO: Implement this test after you implement get_active_ips().

    This test should verify:
      - The method returns a list (not None)
      - Each item in the list is a dict
      - Each dict has required keys: "address", "id", "status"
      - The status value is "active" for all returned IPs
      - All returned IPs fall within the queried prefix

    Hints:
      - Use a prefix that you KNOW has active IPs in your NetBox instance
      - The test prefix should match what's seeded in your lab setup
    """
    # TODO: Update this prefix to match your lab environment
    test_prefix = "10.0.1.0/24"

    # TODO: Uncomment and complete the assertions below
    # results = await netbox_client.get_active_ips(test_prefix)
    #
    # # Basic type checks
    # assert isinstance(results, list), "Should return a list"
    # assert len(results) > 0, f"Expected active IPs in {test_prefix}"
    #
    # # Validate structure of each result
    # for ip_entry in results:
    #     assert isinstance(ip_entry, dict), "Each entry should be a dict"
    #     assert "address" in ip_entry, "Each entry needs an 'address' field"
    #     assert "id" in ip_entry, "Each entry needs an 'id' field"
    #     assert "status" in ip_entry, "Each entry needs a 'status' field"

    pytest.skip("TODO: Implement this test after implementing get_active_ips()")


# ---------------------------------------------------------------------------
# Test: deprecate_ip (TODO — implement after you build the method)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_deprecate_ip(netbox_client: NetBoxClient) -> None:
    """Test that deprecate_ip() changes an IP's status to deprecated.

    TODO: Implement this test after you implement deprecate_ip().

    CAUTION: This test MODIFIES data in NetBox! Use a test IP that
    you can safely change, or re-activate it after the test.

    This test should verify:
      - The method returns a dict (the updated IP object)
      - The returned dict shows status as "deprecated"
      - The IP was actually changed in NetBox (verify with a follow-up query)

    Hints:
      - Create a test IP in NetBox specifically for this test
      - Or use get_active_ips() first to find an IP you can safely deprecate
      - Consider re-activating the IP after the test to keep your lab clean
    """
    # TODO: Uncomment and complete this test
    # WARNING: This modifies data — use a safe test IP!
    #
    # test_ip_id = 1  # Replace with a real IP ID from your NetBox
    #
    # result = await netbox_client.deprecate_ip(test_ip_id)
    #
    # assert isinstance(result, dict), "Should return a dict"
    # assert result.get("status", {}).get("value") == "deprecated", (
    #     "Status should be 'deprecated'"
    # )

    pytest.skip("TODO: Implement this test after implementing deprecate_ip()")
