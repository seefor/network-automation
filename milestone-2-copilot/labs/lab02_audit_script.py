#!/usr/bin/env python3
"""
Lab 2: Device Audit Script (Skeleton)

Audit multiple Arista EOS switches for best-practice configurations:
- NTP: at least one NTP server configured
- DNS: at least one name-server configured
- SNMP: no default/weak community strings
- Syslog: at least one logging host configured

Usage:
    python lab02_audit_script.py --inventory inventory.yml

Instructions:
    Use an LLM to help you complete the TODO sections below.
    Each TODO has a description of what the code should do.
    After completing each section, test against your lab switches.

Dependencies:
    pip install netmiko pyyaml rich
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import yaml
from netmiko import ConnectHandler, NetmikoAuthenticationException, NetmikoTimeoutException
from rich.console import Console
from rich.table import Table


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class CheckStatus(Enum):
    """Result of a single audit check."""
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"


@dataclass
class CheckResult:
    """Stores the outcome of one audit check on one device."""
    check_name: str
    status: CheckStatus
    detail: str = ""


@dataclass
class DeviceAudit:
    """Stores all audit results for a single device."""
    hostname: str
    ip: str
    results: list[CheckResult] = field(default_factory=list)
    reachable: bool = True


@dataclass
class DeviceInfo:
    """Connection parameters for a single device."""
    hostname: str
    ip: str
    username: str
    password: str
    device_type: str = "arista_eos"


# ---------------------------------------------------------------------------
# Inventory Loading
# ---------------------------------------------------------------------------

def load_inventory(inventory_path: Path) -> list[DeviceInfo]:
    """Load device inventory from a YAML file.

    Expected YAML structure:
        devices:
          - hostname: spine1
            ip: 172.20.20.11
            username: admin
            password: admin
            device_type: arista_eos

    If username/password are not in the YAML, fall back to the
    DEVICE_USERNAME and DEVICE_PASSWORD environment variables.
    """
    # TODO 1: Load the YAML file and return a list of DeviceInfo objects.
    #
    # Steps:
    #   1. Read the YAML file at inventory_path using yaml.safe_load()
    #   2. Iterate over the "devices" list in the YAML
    #   3. For each device, create a DeviceInfo dataclass instance
    #   4. Use the YAML values for hostname, ip, device_type
    #   5. For username and password, check the YAML first, then fall back
    #      to os.environ.get("DEVICE_USERNAME", "admin") and same for password
    #   6. Return the list of DeviceInfo objects
    #
    # Raise FileNotFoundError if the inventory file does not exist.
    # Raise ValueError if the YAML is missing the "devices" key.

    raise NotImplementedError("TODO 1: Implement load_inventory()")


# ---------------------------------------------------------------------------
# Device Connection
# ---------------------------------------------------------------------------

def connect_to_device(device: DeviceInfo) -> ConnectHandler | None:
    """Establish an SSH connection to a device via Netmiko.

    Returns a ConnectHandler on success, None on failure.
    """
    # TODO 2: Connect to the device using Netmiko.
    #
    # Steps:
    #   1. Build the Netmiko connection dictionary from the DeviceInfo fields:
    #      device_type, host (from ip), username, password
    #   2. Set a timeout of 10 seconds and add it to the connection dict
    #   3. Try to create a ConnectHandler with the connection dict
    #   4. Catch NetmikoTimeoutException -> print a warning, return None
    #   5. Catch NetmikoAuthenticationException -> print a warning, return None
    #   6. On success, return the ConnectHandler

    raise NotImplementedError("TODO 2: Implement connect_to_device()")


# ---------------------------------------------------------------------------
# Audit Check Functions
# ---------------------------------------------------------------------------

def check_ntp(connection: ConnectHandler) -> CheckResult:
    """Check that at least one NTP server is configured.

    Run "show running-config section ntp" and look for lines matching
    "ntp server <ip>".
    """
    # TODO 3: Implement NTP check.
    #
    # Steps:
    #   1. Run "show running-config section ntp" using connection.send_command()
    #   2. Look for lines that start with "ntp server"
    #   3. If at least one NTP server line is found:
    #      - Return CheckResult with status=PASS and detail listing the servers
    #   4. If no NTP server lines are found:
    #      - Return CheckResult with status=FAIL and detail="No NTP servers configured"
    #
    # The check_name should be "NTP".

    raise NotImplementedError("TODO 3: Implement check_ntp()")


def check_dns(connection: ConnectHandler) -> CheckResult:
    """Check that at least one DNS name-server is configured.

    Run "show running-config section name-server" and look for
    "ip name-server" lines.
    """
    # TODO 4: Implement DNS check.
    #
    # Steps:
    #   1. Run "show running-config section name-server" using send_command()
    #   2. Look for lines containing "ip name-server"
    #   3. Extract the server IPs from those lines
    #   4. Return PASS if at least one name-server is found, FAIL otherwise
    #   5. Include the found servers (or "No DNS servers configured") in detail
    #
    # The check_name should be "DNS".

    raise NotImplementedError("TODO 4: Implement check_dns()")


def check_snmp(connection: ConnectHandler) -> CheckResult:
    """Check that no default/weak SNMP community strings are in use.

    Run "show running-config section snmp" and flag community strings
    that match known-bad values.
    """
    # TODO 5: Implement SNMP check.
    #
    # Steps:
    #   1. Define a set of bad community strings: {"public", "private",
    #      "community", "test", "default"}
    #   2. Run "show running-config section snmp" using send_command()
    #   3. Parse lines matching "snmp-server community <string>"
    #   4. Check if any parsed community string is in the bad set
    #   5. Return FAIL if any bad strings found, with detail listing them
    #   6. Return PASS if no bad strings found
    #   7. If no SNMP config exists at all, return PASS with detail
    #      "No SNMP communities configured"
    #
    # The check_name should be "SNMP".

    raise NotImplementedError("TODO 5: Implement check_snmp()")


def check_syslog(connection: ConnectHandler) -> CheckResult:
    """Check that at least one syslog (logging) host is configured.

    Run "show running-config section logging" and look for
    "logging host <ip>" lines.
    """
    # TODO 6: Implement syslog check.
    #
    # Steps:
    #   1. Run "show running-config section logging" using send_command()
    #   2. Look for lines containing "logging host"
    #   3. Extract the logging host IPs
    #   4. Return PASS if at least one logging host is found, FAIL otherwise
    #   5. Include found hosts (or "No syslog hosts configured") in detail
    #
    # The check_name should be "Syslog".

    raise NotImplementedError("TODO 6: Implement check_syslog()")


# ---------------------------------------------------------------------------
# Audit Orchestration
# ---------------------------------------------------------------------------

# The list of all checks to run. Each is a callable that takes a
# ConnectHandler and returns a CheckResult.
AUDIT_CHECKS: list = [check_ntp, check_dns, check_snmp, check_syslog]


def audit_device(device: DeviceInfo) -> DeviceAudit:
    """Run all audit checks against a single device."""
    # TODO 7: Orchestrate the audit for one device.
    #
    # Steps:
    #   1. Create a DeviceAudit instance with hostname and ip from device
    #   2. Call connect_to_device(device) to get a connection
    #   3. If connection is None, set audit.reachable = False and return
    #   4. Iterate over AUDIT_CHECKS, calling each with the connection
    #   5. Append each CheckResult to audit.results
    #   6. Wrap each check call in a try/except to catch unexpected errors
    #      - On exception, append a CheckResult with status=ERROR and
    #        the exception message as detail
    #   7. Disconnect from the device (connection.disconnect())
    #   8. Return the DeviceAudit

    raise NotImplementedError("TODO 7: Implement audit_device()")


# ---------------------------------------------------------------------------
# Output / Reporting
# ---------------------------------------------------------------------------

def print_results(audits: list[DeviceAudit]) -> None:
    """Print a summary table of all audit results using rich."""
    # TODO 8: Build and print a rich Table.
    #
    # Steps:
    #   1. Create a rich Console and Table
    #   2. Add columns: "Device", then one column per check name (NTP, DNS,
    #      SNMP, Syslog)
    #   3. For each DeviceAudit:
    #      a. If not reachable, add a row with "UNREACHABLE" in every column
    #      b. Otherwise, add a row with the status of each check
    #   4. Color-code cells: green for PASS, red for FAIL, yellow for ERROR
    #   5. Print the table to the console
    #
    # Use rich markup for colors, e.g.:
    #   "[green]PASS[/green]" or "[red]FAIL[/red]"

    raise NotImplementedError("TODO 8: Implement print_results()")


def save_json_report(audits: list[DeviceAudit], output_path: Path) -> None:
    """Save audit results to a JSON file."""
    # TODO 9: Serialize audit results to JSON.
    #
    # Steps:
    #   1. Build a list of dicts, one per device:
    #      {
    #        "hostname": "spine1",
    #        "ip": "172.20.20.11",
    #        "reachable": true,
    #        "checks": {
    #          "NTP": {"status": "PASS", "detail": "..."},
    #          "DNS": {"status": "FAIL", "detail": "..."},
    #          ...
    #        }
    #      }
    #   2. Write the list to output_path as formatted JSON (indent=2)
    #   3. Print a message confirming where the report was saved

    raise NotImplementedError("TODO 9: Implement save_json_report()")


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Audit Arista EOS switches for best-practice configurations."
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path(__file__).parent / "inventory.yml",
        help="Path to the YAML inventory file (default: inventory.yml in script dir)",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("audit_report.json"),
        help="Path for JSON report output (default: audit_report.json)",
    )
    return parser.parse_args()


def main() -> int:
    """Main entry point. Returns 0 if all checks pass, 1 otherwise."""
    args = parse_args()

    # Load inventory
    try:
        devices: list[DeviceInfo] = load_inventory(args.inventory)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error loading inventory: {exc}", file=sys.stderr)
        return 1

    print(f"Auditing {len(devices)} device(s)...\n")

    # Run audits
    audits: list[DeviceAudit] = []
    for device in devices:
        print(f"  -> {device.hostname} ({device.ip})")
        audit = audit_device(device)
        audits.append(audit)

    # Display results
    print()
    print_results(audits)

    # Save JSON report
    save_json_report(audits, args.json_output)

    # Determine exit code: 1 if any check failed or any device unreachable
    any_failures: bool = any(
        not audit.reachable
        or any(r.status != CheckStatus.PASS for r in audit.results)
        for audit in audits
    )
    return 1 if any_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
