#!/usr/bin/env python3
"""
Lab 2: Device Audit Script (Solution)

Audit multiple Arista EOS switches for best-practice configurations:
- NTP: at least one NTP server configured
- DNS: at least one name-server configured
- SNMP: no default/weak community strings
- Syslog: at least one logging host configured

Usage:
    python lab02_audit_script.py --inventory inventory.yml

Dependencies:
    pip install netmiko pyyaml rich
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable

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
    """
    if not inventory_path.exists():
        raise FileNotFoundError(f"Inventory file not found: {inventory_path}")

    raw: dict = yaml.safe_load(inventory_path.read_text())

    if "devices" not in raw:
        raise ValueError(f"Inventory YAML missing 'devices' key: {inventory_path}")

    default_user: str = os.environ.get("DEVICE_USERNAME", "admin")
    default_pass: str = os.environ.get("DEVICE_PASSWORD", "admin")

    devices: list[DeviceInfo] = []
    for entry in raw["devices"]:
        devices.append(
            DeviceInfo(
                hostname=entry["hostname"],
                ip=entry["ip"],
                username=entry.get("username", default_user),
                password=entry.get("password", default_pass),
                device_type=entry.get("device_type", "arista_eos"),
            )
        )

    return devices


# ---------------------------------------------------------------------------
# Device Connection
# ---------------------------------------------------------------------------

def connect_to_device(device: DeviceInfo) -> ConnectHandler | None:
    """Establish an SSH connection to a device via Netmiko.

    Returns a ConnectHandler on success, None on failure.
    """
    conn_params: dict[str, str | int] = {
        "device_type": device.device_type,
        "host": device.ip,
        "username": device.username,
        "password": device.password,
        "timeout": 10,
    }

    try:
        connection: ConnectHandler = ConnectHandler(**conn_params)
        return connection
    except NetmikoTimeoutException:
        print(f"    [WARN] Timeout connecting to {device.hostname} ({device.ip})")
        return None
    except NetmikoAuthenticationException:
        print(f"    [WARN] Auth failed for {device.hostname} ({device.ip})")
        return None


# ---------------------------------------------------------------------------
# Audit Check Functions
# ---------------------------------------------------------------------------

def check_ntp(connection: ConnectHandler) -> CheckResult:
    """Check that at least one NTP server is configured."""
    output: str = connection.send_command("show running-config section ntp")

    servers: list[str] = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("ntp server"):
            # "ntp server 10.100.100.100" -> extract the IP/hostname
            parts: list[str] = line.split()
            if len(parts) >= 3:
                servers.append(parts[2])

    if servers:
        return CheckResult(
            check_name="NTP",
            status=CheckStatus.PASS,
            detail=f"Servers: {', '.join(servers)}",
        )
    return CheckResult(
        check_name="NTP",
        status=CheckStatus.FAIL,
        detail="No NTP servers configured",
    )


def check_dns(connection: ConnectHandler) -> CheckResult:
    """Check that at least one DNS name-server is configured."""
    output: str = connection.send_command("show running-config section name-server")

    servers: list[str] = []
    for line in output.splitlines():
        line = line.strip()
        if "ip name-server" in line:
            # "ip name-server vrf default 8.8.8.8" or "ip name-server 8.8.8.8"
            parts: list[str] = line.split()
            # The IP is always the last element
            servers.append(parts[-1])

    if servers:
        return CheckResult(
            check_name="DNS",
            status=CheckStatus.PASS,
            detail=f"Servers: {', '.join(servers)}",
        )
    return CheckResult(
        check_name="DNS",
        status=CheckStatus.FAIL,
        detail="No DNS servers configured",
    )


def check_snmp(connection: ConnectHandler) -> CheckResult:
    """Check that no default/weak SNMP community strings are in use."""
    bad_communities: set[str] = {"public", "private", "community", "test", "default"}

    output: str = connection.send_command("show running-config section snmp")

    found_communities: list[str] = []
    flagged: list[str] = []

    for line in output.splitlines():
        line = line.strip()
        # Match "snmp-server community <string> ..."
        match: re.Match[str] | None = re.match(
            r"snmp-server\s+community\s+(\S+)", line
        )
        if match:
            community: str = match.group(1)
            found_communities.append(community)
            if community.lower() in bad_communities:
                flagged.append(community)

    if not found_communities:
        return CheckResult(
            check_name="SNMP",
            status=CheckStatus.PASS,
            detail="No SNMP communities configured",
        )

    if flagged:
        return CheckResult(
            check_name="SNMP",
            status=CheckStatus.FAIL,
            detail=f"Weak communities found: {', '.join(flagged)}",
        )

    return CheckResult(
        check_name="SNMP",
        status=CheckStatus.PASS,
        detail=f"{len(found_communities)} community string(s), none flagged",
    )


def check_syslog(connection: ConnectHandler) -> CheckResult:
    """Check that at least one syslog (logging) host is configured."""
    output: str = connection.send_command("show running-config section logging")

    hosts: list[str] = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("logging host"):
            parts: list[str] = line.split()
            if len(parts) >= 3:
                hosts.append(parts[2])

    if hosts:
        return CheckResult(
            check_name="Syslog",
            status=CheckStatus.PASS,
            detail=f"Hosts: {', '.join(hosts)}",
        )
    return CheckResult(
        check_name="Syslog",
        status=CheckStatus.FAIL,
        detail="No syslog hosts configured",
    )


# ---------------------------------------------------------------------------
# Audit Orchestration
# ---------------------------------------------------------------------------

AUDIT_CHECKS: list[Callable[[ConnectHandler], CheckResult]] = [
    check_ntp,
    check_dns,
    check_snmp,
    check_syslog,
]


def audit_device(device: DeviceInfo) -> DeviceAudit:
    """Run all audit checks against a single device."""
    audit = DeviceAudit(hostname=device.hostname, ip=device.ip)

    connection: ConnectHandler | None = connect_to_device(device)
    if connection is None:
        audit.reachable = False
        return audit

    try:
        for check_fn in AUDIT_CHECKS:
            try:
                result: CheckResult = check_fn(connection)
                audit.results.append(result)
            except Exception as exc:
                audit.results.append(
                    CheckResult(
                        check_name=check_fn.__name__.replace("check_", "").upper(),
                        status=CheckStatus.ERROR,
                        detail=str(exc),
                    )
                )
    finally:
        connection.disconnect()

    return audit


# ---------------------------------------------------------------------------
# Output / Reporting
# ---------------------------------------------------------------------------

def _status_markup(status: CheckStatus) -> str:
    """Return a rich-markup string for a check status."""
    color_map: dict[CheckStatus, str] = {
        CheckStatus.PASS: "green",
        CheckStatus.FAIL: "red",
        CheckStatus.ERROR: "yellow",
    }
    color: str = color_map.get(status, "white")
    return f"[{color}]{status.value}[/{color}]"


def print_results(audits: list[DeviceAudit]) -> None:
    """Print a summary table of all audit results using rich."""
    console = Console()
    table = Table(title="Device Audit Results", show_lines=True)

    # Build column list from the check names
    check_names: list[str] = [fn.__name__.replace("check_", "").upper() for fn in AUDIT_CHECKS]

    table.add_column("Device", style="bold cyan", no_wrap=True)
    for name in check_names:
        table.add_column(name, justify="center")

    for audit in audits:
        label: str = f"{audit.hostname}\n({audit.ip})"

        if not audit.reachable:
            table.add_row(label, *["[yellow]UNREACHABLE[/yellow]"] * len(check_names))
            continue

        # Build a lookup from check_name -> CheckResult
        result_map: dict[str, CheckResult] = {r.check_name: r for r in audit.results}

        cells: list[str] = []
        for name in check_names:
            result: CheckResult | None = result_map.get(name)
            if result is None:
                cells.append("[yellow]SKIPPED[/yellow]")
            else:
                cells.append(_status_markup(result.status))

        table.add_row(label, *cells)

    console.print(table)


def save_json_report(audits: list[DeviceAudit], output_path: Path) -> None:
    """Save audit results to a JSON file."""
    report: list[dict] = []

    for audit in audits:
        device_entry: dict = {
            "hostname": audit.hostname,
            "ip": audit.ip,
            "reachable": audit.reachable,
            "checks": {},
        }
        for result in audit.results:
            device_entry["checks"][result.check_name] = {
                "status": result.status.value,
                "detail": result.detail,
            }
        report.append(device_entry)

    output_path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"JSON report saved to: {output_path}")


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
