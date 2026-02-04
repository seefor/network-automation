"""
Device Connector
=================

This module provides SSH-based access to network devices using Netmiko.
It connects to Arista EOS switches/routers to pull live network data.

WHAT YOU NEED TO IMPLEMENT:
  - get_arp_table()      : SSH in, run "show ip arp", parse the output
  - get_interfaces()     : SSH in, run "show ip interface brief", parse the output
  - parse_arp_output()   : Helper to parse raw ARP CLI output into structured dicts

Netmiko documentation: https://github.com/ktbyers/netmiko

Key concepts:
  - Netmiko's ConnectHandler establishes an SSH session
  - send_command() sends a CLI command and returns the text output
  - You parse the raw text output into structured Python dicts
  - Always disconnect when done (use try/finally or context manager)
"""

from __future__ import annotations

import logging

from netmiko import ConnectHandler

logger = logging.getLogger("reclaim-agent.devices")


class DeviceConnector:
    """SSH connector for network devices using Netmiko.

    Usage:
        connector = DeviceConnector(
            hostname="spine1",
            username="admin",
            password="admin",
            device_type="arista_eos",
        )
        arp_entries = connector.get_arp_table()
        interfaces = connector.get_interfaces()
    """

    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        device_type: str = "arista_eos",
        enable_password: str | None = None,
    ) -> None:
        """Initialize the device connector.

        Args:
            hostname:        Hostname or IP of the device to connect to.
            username:        SSH username.
            password:        SSH password.
            device_type:     Netmiko device type string. Default: "arista_eos".
            enable_password: Enable/privileged mode password (if required).
        """
        self.hostname = hostname
        self.device_type = device_type

        # Netmiko connection parameters — passed directly to ConnectHandler
        self.connection_params: dict = {
            "device_type": device_type,
            "host": hostname,
            "username": username,
            "password": password,
        }
        if enable_password:
            self.connection_params["secret"] = enable_password

    # -----------------------------------------------------------------------
    # STUB: get_arp_table
    # -----------------------------------------------------------------------

    def get_arp_table(self) -> list[dict]:
        """Connect to the device via SSH and retrieve the ARP table.

        Returns:
            A list of dicts, each representing an ARP entry:
              [
                  {
                      "ip_address": "10.0.1.5",
                      "mac_address": "00:1a:2b:3c:4d:5e",
                      "interface": "Ethernet1",
                      "age": "0:02:15"
                  },
                  ...
              ]

        Hints:
            - Use ConnectHandler(**self.connection_params) to connect
            - Send the command: "show ip arp"
            - Parse the output using parse_arp_output() helper below
            - ALWAYS disconnect when done (use try/finally)

        Example Arista EOS "show ip arp" output:
            Address         Age (sec)  Hardware Addr   Interface
            10.0.1.1        0:00:05    001a.2b3c.4d5e  Ethernet1
            10.0.1.5        0:02:15    001a.2b3c.4d60  Ethernet2
            10.0.1.10       -          001a.2b3c.4d61  Ethernet3
        """
        # TODO: Implement this method
        # 1. Establish SSH connection using ConnectHandler
        # 2. Send "show ip arp" command
        # 3. Parse the output using parse_arp_output()
        # 4. Disconnect from the device (in a finally block!)
        # 5. Return the parsed ARP entries
        raise NotImplementedError("TODO: Implement get_arp_table")

    # -----------------------------------------------------------------------
    # STUB: get_interfaces
    # -----------------------------------------------------------------------

    def get_interfaces(self) -> list[dict]:
        """Connect to the device via SSH and retrieve interface IP assignments.

        Returns:
            A list of dicts, each representing an interface with an IP:
              [
                  {
                      "interface": "Ethernet1",
                      "ip_address": "10.0.1.1/24",
                      "status": "up",
                      "description": "Uplink to spine1"
                  },
                  ...
              ]

        Hints:
            - Use ConnectHandler(**self.connection_params) to connect
            - Send the command: "show ip interface brief"
            - Parse the tabular output into structured dicts
            - Only include interfaces that have an IP address assigned
            - ALWAYS disconnect when done (use try/finally)

        Example Arista EOS "show ip interface brief" output:
            Interface       IP Address      Status  Protocol  MTU   Description
            Ethernet1       10.0.1.1/24     up      up        1500  Uplink to spine
            Ethernet2       unassigned      up      up        1500
            Loopback0       1.1.1.1/32      up      up        65535 Router ID
        """
        # TODO: Implement this method
        # 1. Establish SSH connection using ConnectHandler
        # 2. Send "show ip interface brief" command
        # 3. Parse the tabular output into a list of dicts
        # 4. Filter out interfaces without an IP (where IP is "unassigned")
        # 5. Disconnect from the device (in a finally block!)
        # 6. Return the list of interface dicts
        raise NotImplementedError("TODO: Implement get_interfaces")


# ---------------------------------------------------------------------------
# STUB: parse_arp_output (helper function)
# ---------------------------------------------------------------------------


def parse_arp_output(raw: str) -> list[dict]:
    """Parse raw "show ip arp" CLI output into structured dicts.

    Args:
        raw: The raw text output from the "show ip arp" command.

    Returns:
        A list of dicts with keys: ip_address, mac_address, interface, age.

    Hints:
        - Skip the header line(s)
        - Split each line by whitespace
        - Handle edge cases: empty lines, partial entries
        - Arista EOS format:
            Address         Age (sec)  Hardware Addr   Interface
            10.0.1.1        0:00:05    001a.2b3c.4d5e  Ethernet1

    Example:
        >>> raw = "Address  Age  Hardware Addr  Interface\\n10.0.1.1  0:05  001a.2b3c.4d5e  Eth1"
        >>> parse_arp_output(raw)
        [{"ip_address": "10.0.1.1", "mac_address": "001a.2b3c.4d5e", "interface": "Eth1", "age": "0:05"}]
    """
    # TODO: Implement this helper function
    # 1. Split the raw output into lines
    # 2. Skip the header line (first line)
    # 3. For each remaining line:
    #    a. Skip empty lines
    #    b. Split by whitespace
    #    c. Extract: ip_address, age, mac_address, interface
    #    d. Append to results list
    # 4. Return the results
    raise NotImplementedError("TODO: Implement parse_arp_output")
