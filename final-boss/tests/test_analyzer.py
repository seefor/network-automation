"""
Tests for the IP Reclamation Analyzer
=======================================

These tests verify your analyzer logic works correctly using MOCK DATA.
No network connectivity is required — these are pure unit tests.

HOW TO RUN:
    uv run pytest tests/test_analyzer.py -v

WHAT'S TESTED:
    - find_stale_ips()            : Does it correctly identify IPs missing from live data?
    - build_reclamation_report()  : Does the report have the right structure and stats?
"""

from __future__ import annotations

import pytest

from reclaim_agent.tools.analyzer import build_reclamation_report, find_stale_ips


# ---------------------------------------------------------------------------
# Mock data — simulates what the real tools would return
# ---------------------------------------------------------------------------

# These are the IPs that NetBox says are allocated (Source of Truth)
MOCK_NETBOX_IPS: list[dict] = [
    {
        "address": "10.0.1.1/24",
        "id": 1,
        "description": "Gateway - spine1 Ethernet1",
        "dns_name": "gw.lab.local",
        "status": {"value": "active", "label": "Active"},
    },
    {
        "address": "10.0.1.5/24",
        "id": 2,
        "description": "Web server",
        "dns_name": "web.lab.local",
        "status": {"value": "active", "label": "Active"},
    },
    {
        "address": "10.0.1.10/24",
        "id": 3,
        "description": "Database server",
        "dns_name": "db.lab.local",
        "status": {"value": "active", "label": "Active"},
    },
    {
        "address": "10.0.1.15/24",
        "id": 4,
        "description": "Old test server - decommed Q3 2024",
        "dns_name": "test-old.lab.local",
        "status": {"value": "active", "label": "Active"},
    },
    {
        "address": "10.0.1.22/24",
        "id": 5,
        "description": "Monitoring agent",
        "dns_name": "",
        "status": {"value": "active", "label": "Active"},
    },
    {
        "address": "10.0.1.30/24",
        "id": 6,
        "description": "Dev sandbox - project cancelled",
        "dns_name": "",
        "status": {"value": "active", "label": "Active"},
    },
]

# These are the ARP entries from the live network
# NOTE: 10.0.1.15, 10.0.1.22, and 10.0.1.30 are NOT in ARP (they're stale!)
MOCK_ARP_ENTRIES: list[dict] = [
    {
        "ip_address": "10.0.1.1",
        "mac_address": "00:1a:2b:3c:4d:01",
        "interface": "Ethernet1",
        "age": "0:00:05",
    },
    {
        "ip_address": "10.0.1.5",
        "mac_address": "00:1a:2b:3c:4d:05",
        "interface": "Ethernet2",
        "age": "0:01:30",
    },
    {
        "ip_address": "10.0.1.10",
        "mac_address": "00:1a:2b:3c:4d:10",
        "interface": "Ethernet3",
        "age": "0:05:22",
    },
]

# These are IPs assigned to device interfaces
MOCK_INTERFACE_IPS: list[dict] = [
    {
        "interface": "Ethernet1",
        "ip_address": "10.0.1.1/24",
        "status": "up",
        "description": "Gateway interface",
    },
    {
        "interface": "Loopback0",
        "ip_address": "1.1.1.1/32",
        "status": "up",
        "description": "Router ID",
    },
]


# ---------------------------------------------------------------------------
# Test: find_stale_ips
# ---------------------------------------------------------------------------


class TestFindStaleIps:
    """Tests for the find_stale_ips() function."""

    def test_identifies_stale_ips(self) -> None:
        """Test that IPs in NetBox but NOT in ARP or interfaces are flagged as stale.

        With the mock data above:
          - 10.0.1.1  is in ARP and on an interface  -> NOT stale
          - 10.0.1.5  is in ARP                      -> NOT stale
          - 10.0.1.10 is in ARP                      -> NOT stale
          - 10.0.1.15 is NOT in ARP, NOT on interface -> STALE
          - 10.0.1.22 is NOT in ARP, NOT on interface -> STALE
          - 10.0.1.30 is NOT in ARP, NOT on interface -> STALE

        Expected: 3 stale IPs (10.0.1.15, 10.0.1.22, 10.0.1.30)
        """
        stale = find_stale_ips(MOCK_NETBOX_IPS, MOCK_ARP_ENTRIES, MOCK_INTERFACE_IPS)

        # -- Check count --
        assert len(stale) == 3, (
            f"Expected 3 stale IPs, got {len(stale)}. "
            "IPs 10.0.1.15, 10.0.1.22, and 10.0.1.30 should be stale."
        )

        # -- Check that the right IPs are flagged --
        stale_addresses = {entry["address"] for entry in stale}
        expected_stale = {"10.0.1.15/24", "10.0.1.22/24", "10.0.1.30/24"}
        assert stale_addresses == expected_stale, (
            f"Wrong IPs flagged as stale.\n"
            f"  Expected: {expected_stale}\n"
            f"  Got:      {stale_addresses}"
        )

        # -- Check structure of each stale entry --
        for entry in stale:
            assert "address" in entry, "Each stale entry must have 'address'"
            assert "netbox_id" in entry, "Each stale entry must have 'netbox_id'"
            assert "confidence" in entry, "Each stale entry must have 'confidence'"
            assert "reason" in entry, "Each stale entry must have 'reason'"

    def test_no_stale_when_all_active(self) -> None:
        """Test that no IPs are flagged stale when ALL are seen in ARP.

        If every NetBox IP appears in the ARP table, the stale list should be empty.
        """
        # Create ARP entries for ALL NetBox IPs
        all_active_arp = [
            {"ip_address": "10.0.1.1", "mac_address": "aa:bb:cc:dd:ee:01", "interface": "Eth1", "age": "0:01"},
            {"ip_address": "10.0.1.5", "mac_address": "aa:bb:cc:dd:ee:05", "interface": "Eth2", "age": "0:02"},
            {"ip_address": "10.0.1.10", "mac_address": "aa:bb:cc:dd:ee:10", "interface": "Eth3", "age": "0:03"},
            {"ip_address": "10.0.1.15", "mac_address": "aa:bb:cc:dd:ee:15", "interface": "Eth4", "age": "0:04"},
            {"ip_address": "10.0.1.22", "mac_address": "aa:bb:cc:dd:ee:22", "interface": "Eth5", "age": "0:05"},
            {"ip_address": "10.0.1.30", "mac_address": "aa:bb:cc:dd:ee:30", "interface": "Eth6", "age": "0:06"},
        ]

        stale = find_stale_ips(MOCK_NETBOX_IPS, all_active_arp, MOCK_INTERFACE_IPS)

        assert len(stale) == 0, (
            f"Expected 0 stale IPs when all are in ARP, got {len(stale)}"
        )

    def test_empty_inputs(self) -> None:
        """Test that empty inputs return empty results."""
        stale = find_stale_ips([], [], [])
        assert stale == [], "Empty NetBox list should produce empty stale list"

    def test_all_stale_when_no_arp(self) -> None:
        """Test that ALL IPs are stale when ARP and interface lists are empty."""
        stale = find_stale_ips(MOCK_NETBOX_IPS, [], [])

        assert len(stale) == len(MOCK_NETBOX_IPS), (
            f"All {len(MOCK_NETBOX_IPS)} IPs should be stale when ARP is empty, "
            f"got {len(stale)}"
        )


# ---------------------------------------------------------------------------
# Test: build_reclamation_report
# ---------------------------------------------------------------------------


class TestBuildReclamationReport:
    """Tests for the build_reclamation_report() function."""

    def test_report_structure(self) -> None:
        """Test that the report has all required fields and correct structure.

        The report should contain:
          - report_id: a unique string identifier
          - generated_at: ISO-format timestamp
          - prefix: the audited prefix
          - summary: dict with total_allocated, total_stale, reclamation_rate
          - stale_ips: the list of stale IPs
          - recommended_action: a string recommendation
        """
        mock_stale = [
            {
                "address": "10.0.1.15/24",
                "netbox_id": 4,
                "last_seen": "unknown",
                "device": "none",
                "confidence": "high",
                "reason": "Not found in any ARP table or device interface",
            },
            {
                "address": "10.0.1.22/24",
                "netbox_id": 5,
                "last_seen": "unknown",
                "device": "none",
                "confidence": "high",
                "reason": "Not found in any ARP table or device interface",
            },
        ]

        report = build_reclamation_report(
            stale_ips=mock_stale,
            prefix="10.0.1.0/24",
            total_allocated=6,
        )

        # -- Check top-level fields exist --
        assert "report_id" in report, "Report must have a 'report_id'"
        assert "generated_at" in report, "Report must have a 'generated_at' timestamp"
        assert "prefix" in report, "Report must have a 'prefix'"
        assert "summary" in report, "Report must have a 'summary'"
        assert "stale_ips" in report, "Report must have a 'stale_ips' list"
        assert "recommended_action" in report, "Report must have a 'recommended_action'"

        # -- Check prefix value --
        assert report["prefix"] == "10.0.1.0/24", "Prefix should match input"

        # -- Check summary stats --
        summary = report["summary"]
        assert summary["total_allocated"] == 6, "total_allocated should be 6"
        assert summary["total_stale"] == 2, "total_stale should be 2"

        # Reclamation rate: 2 stale / 6 allocated = 33.33%
        expected_rate = (2 / 6) * 100
        assert abs(summary["reclamation_rate"] - expected_rate) < 0.01, (
            f"reclamation_rate should be ~{expected_rate:.2f}%, "
            f"got {summary['reclamation_rate']}"
        )

        # -- Check stale_ips list --
        assert len(report["stale_ips"]) == 2, "Should have 2 stale IPs in report"

    def test_report_with_no_stale_ips(self) -> None:
        """Test report generation when there are no stale IPs (clean network)."""
        report = build_reclamation_report(
            stale_ips=[],
            prefix="10.0.1.0/24",
            total_allocated=6,
        )

        assert report["summary"]["total_stale"] == 0, "total_stale should be 0"
        assert report["summary"]["reclamation_rate"] == 0.0, "reclamation_rate should be 0%"
        assert len(report["stale_ips"]) == 0, "stale_ips list should be empty"
