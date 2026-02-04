"""
Reclaim Agent MCP Server
=========================

This is the main MCP server file. It exposes tools that an AI agent (like Claude)
can call to investigate and reclaim unused IP addresses from your network.

HOW THIS WORKS:
  - The server registers tools using the @mcp.tool() decorator.
  - Each tool is callable by an AI agent via the Model Context Protocol.
  - The AI agent decides WHEN and HOW to call these tools based on the user's request.

WHAT'S PROVIDED:
  - One fully working example tool: get_netbox_version()
  - Six tool stubs that YOU need to implement (marked with TODO)

YOUR MISSION:
  Implement the six stub tools so the AI agent can:
    1. Query NetBox for allocated IPs in a prefix
    2. SSH into devices to pull ARP tables
    3. SSH into devices to pull interface data
    4. Cross-reference Source-of-Truth vs live network state
    5. Generate a structured reclamation report
    6. Execute reclamation (with human-in-the-loop approval!)

GETTING STARTED:
  1. Copy .env.example to .env and fill in your credentials
  2. Implement the tools one at a time, starting with list_allocated_ips
  3. Test each tool individually before moving to the cross-reference tools
  4. The compare and report tools build on the earlier ones — implement those last

RUN THE SERVER:
  uv run reclaim-agent
"""

from __future__ import annotations

import logging

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from reclaim_agent.tools.netbox import NetBoxClient
from reclaim_agent.utils.config import Settings

# ---------------------------------------------------------------------------
# Bootstrap: load .env file and application settings
# ---------------------------------------------------------------------------
load_dotenv()  # Reads .env file into environment variables
settings = Settings()  # Validates and parses env vars via Pydantic

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("reclaim-agent")

# ---------------------------------------------------------------------------
# Create the MCP server instance
# ---------------------------------------------------------------------------
mcp = FastMCP("reclaim-agent")

# ---------------------------------------------------------------------------
# Shared clients — reused across tool invocations
# ---------------------------------------------------------------------------
netbox = NetBoxClient(url=settings.NETBOX_URL, token=settings.NETBOX_TOKEN)


# ============================================================================
# EXAMPLE TOOL (fully implemented — use this as a reference)
# ============================================================================


@mcp.tool()
async def get_netbox_version() -> str:
    """Return the version of the connected NetBox instance.

    This is a health-check / smoke-test tool. Use it to verify that the
    MCP server can reach NetBox and that the API token is valid.

    Returns:
        A string like "4.2.3" representing the NetBox version.
    """
    logger.info("Fetching NetBox version...")
    version = await netbox.get_version()
    logger.info("NetBox version: %s", version)
    return f"NetBox version: {version}"


# ============================================================================
# TOOL 1: list_allocated_ips
# ============================================================================


@mcp.tool()
async def list_allocated_ips(prefix: str) -> list[dict]:
    """Query NetBox for all IP addresses with status 'Active' in a given prefix.

    This is the Source-of-Truth query. NetBox tracks which IPs are allocated,
    and this tool retrieves that list for a specific CIDR prefix.

    Args:
        prefix: A CIDR prefix string, e.g. "10.0.1.0/24".
                 This is the subnet you want to audit.

    Returns:
        A list of dicts, each representing an allocated IP. Each dict should
        contain at minimum:
          - "address": str      (e.g. "10.0.1.5/24")
          - "id": int           (NetBox IP address object ID)
          - "status": str       (should be "active")
          - "description": str  (what the IP is used for)
          - "dns_name": str     (reverse DNS if configured)

    Implementation hints:
        - Use the NetBoxClient.get_active_ips() method from tools/netbox.py
        - The NetBox API endpoint is: /api/ipam/ip-addresses/?parent={prefix}&status=active
        - Handle pagination if the prefix has many IPs
    """
    # TODO: Implement this tool
    # Steps:
    #   1. Call netbox.get_active_ips(prefix) to query the NetBox API
    #   2. Return the list of IP address objects
    #   3. Handle errors gracefully (return meaningful error messages)
    raise NotImplementedError("TODO: Implement list_allocated_ips")


# ============================================================================
# TOOL 2: get_device_arp_table
# ============================================================================


@mcp.tool()
async def get_device_arp_table(hostname: str) -> list[dict]:
    """SSH into a network device and retrieve its ARP table.

    The ARP table shows which IP addresses are actively communicating on
    the network. If an IP appears in ARP, it was recently active.

    Args:
        hostname: The hostname or IP address of the network device to query.
                   Example: "spine1" or "192.168.1.1"

    Returns:
        A list of dicts, each representing an ARP entry. Each dict should
        contain at minimum:
          - "ip_address": str   (e.g. "10.0.1.5")
          - "mac_address": str  (e.g. "00:1a:2b:3c:4d:5e")
          - "interface": str    (e.g. "Ethernet1")
          - "age": str          (e.g. "0:02:15" or "static")

    Implementation hints:
        - Use DeviceConnector from tools/devices.py
        - The Netmiko command for Arista EOS is: "show ip arp"
        - Parse the raw CLI output into structured dicts
        - Remember to disconnect from the device when done!
    """
    # TODO: Implement this tool
    # Steps:
    #   1. Create a DeviceConnector instance with credentials from settings
    #   2. Call connector.get_arp_table() to SSH in and pull ARP data
    #   3. Return the parsed ARP entries as a list of dicts
    #   4. Handle connection errors (device unreachable, auth failure, etc.)
    raise NotImplementedError("TODO: Implement get_device_arp_table")


# ============================================================================
# TOOL 3: get_device_interfaces
# ============================================================================


@mcp.tool()
async def get_device_interfaces(hostname: str) -> list[dict]:
    """SSH into a network device and retrieve its interface IP assignments.

    This shows which IPs are configured on the device's interfaces.
    These IPs are definitely in use (they're assigned to live interfaces).

    Args:
        hostname: The hostname or IP address of the network device to query.
                   Example: "leaf1" or "192.168.1.2"

    Returns:
        A list of dicts, each representing an interface. Each dict should
        contain at minimum:
          - "interface": str      (e.g. "Ethernet1")
          - "ip_address": str     (e.g. "10.0.1.1/24")
          - "status": str         (e.g. "up" or "down")
          - "description": str    (interface description if set)

    Implementation hints:
        - Use DeviceConnector from tools/devices.py
        - The Netmiko command for Arista EOS is: "show ip interface brief"
        - Parse the raw CLI output into structured dicts
        - Only include interfaces that have an IP assigned
    """
    # TODO: Implement this tool
    # Steps:
    #   1. Create a DeviceConnector instance with credentials from settings
    #   2. Call connector.get_interfaces() to SSH in and pull interface data
    #   3. Return the parsed interface data as a list of dicts
    #   4. Handle connection errors gracefully
    raise NotImplementedError("TODO: Implement get_device_interfaces")


# ============================================================================
# TOOL 4: compare_sot_vs_live
# ============================================================================


@mcp.tool()
async def compare_sot_vs_live(prefix: str) -> dict:
    """Cross-reference NetBox allocations against live network data.

    This is the CORE analysis tool. It answers the question:
    "Which IPs does NetBox say are allocated, but the network says are NOT in use?"

    The tool calls the earlier tools internally to gather data, then compares.

    Args:
        prefix: A CIDR prefix string, e.g. "10.0.1.0/24".

    Returns:
        A dict with the analysis results:
          {
              "prefix": "10.0.1.0/24",
              "total_allocated": 25,       # IPs NetBox says are active
              "total_seen_in_arp": 20,     # IPs that appeared in ARP tables
              "total_on_interfaces": 3,    # IPs assigned to device interfaces
              "potentially_stale": [       # IPs allocated but NOT seen live
                  {"address": "10.0.1.15/24", "id": 42, ...},
                  ...
              ],
              "confirmed_active": [        # IPs that ARE seen live
                  {"address": "10.0.1.1/24", "id": 10, ...},
                  ...
              ]
          }

    Implementation hints:
        - Call list_allocated_ips() to get NetBox data
        - Call get_device_arp_table() for relevant devices (you need to figure
          out which devices to query — look at the prefix's gateway or VLAN)
        - Call get_device_interfaces() for the same devices
        - Use the find_stale_ips() function from tools/analyzer.py to compare
        - This tool ties everything together — implement it LAST
    """
    # TODO: Implement this tool
    # Steps:
    #   1. Call list_allocated_ips(prefix) to get Source-of-Truth data
    #   2. Determine which devices to query (e.g., the prefix's default gateway)
    #   3. Call get_device_arp_table() and get_device_interfaces() for each device
    #   4. Use find_stale_ips() from tools/analyzer.py to identify mismatches
    #   5. Return a structured comparison dict
    raise NotImplementedError("TODO: Implement compare_sot_vs_live")


# ============================================================================
# TOOL 5: generate_reclamation_report
# ============================================================================


@mcp.tool()
async def generate_reclamation_report(prefix: str) -> dict:
    """Generate a structured JSON report of stale IPs that can be reclaimed.

    This tool builds on compare_sot_vs_live() and produces a formal report
    suitable for review before executing reclamation.

    Args:
        prefix: A CIDR prefix string, e.g. "10.0.1.0/24".

    Returns:
        A structured dict report:
          {
              "report_id": "reclaim-20250115-143022",
              "generated_at": "2025-01-15T14:30:22Z",
              "prefix": "10.0.1.0/24",
              "summary": {
                  "total_allocated": 25,
                  "total_stale": 5,
                  "reclamation_rate": 20.0
              },
              "stale_ips": [
                  {
                      "address": "10.0.1.15/24",
                      "netbox_id": 42,
                      "last_seen": "unknown",
                      "device": "none",
                      "confidence": "high",
                      "reason": "Not found in any ARP table or interface"
                  },
                  ...
              ],
              "recommended_action": "Review stale IPs and execute reclamation"
          }

    Implementation hints:
        - Call compare_sot_vs_live() to get the raw comparison data
        - Use build_reclamation_report() from tools/analyzer.py to format it
        - Add a unique report ID (timestamp-based) and metadata
    """
    # TODO: Implement this tool
    # Steps:
    #   1. Call compare_sot_vs_live(prefix) to get the comparison data
    #   2. Extract the stale IPs from the comparison
    #   3. Use build_reclamation_report() from tools/analyzer.py to format
    #   4. Return the structured report dict
    raise NotImplementedError("TODO: Implement generate_reclamation_report")


# ============================================================================
# TOOL 6: execute_reclamation
# ============================================================================


@mcp.tool()
async def execute_reclamation(ip_addresses: list[str]) -> dict:
    """Change the status of IP addresses in NetBox from Active to Deprecated.

    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    CRITICAL: This tool MODIFIES data in NetBox. It MUST include a
    human-in-the-loop (HITL) approval gate before making any changes.
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    The HITL pattern for MCP tools:
        1. First call: Return a confirmation prompt listing what will change.
           The AI agent will show this to the user and ask for approval.
        2. The user confirms (or denies) through the AI agent.
        3. Second call (after confirmation): Execute the actual changes.

    Since MCP tools are stateless, you can implement the HITL gate by:
        - Requiring a "confirm" parameter or a special confirmation token
        - Or by splitting into a "dry run" that shows changes and a separate
          execution path

    Args:
        ip_addresses: List of IP address strings to deprecate.
                       Example: ["10.0.1.15/24", "10.0.1.22/24"]

    Returns:
        A dict with the results:
          {
              "action": "reclamation",
              "status": "completed" | "pending_confirmation" | "failed",
              "results": [
                  {
                      "address": "10.0.1.15/24",
                      "old_status": "active",
                      "new_status": "deprecated",
                      "success": true
                  },
                  ...
              ],
              "message": "Successfully deprecated 2 of 2 IP addresses"
          }

    Implementation hints:
        - Look up each IP in NetBox to get its object ID
        - Use NetBoxClient.deprecate_ip() to change the status
        - Log every change for audit purposes
        - If ANY IP fails, report it but continue with the others
        - The HITL gate is the MOST IMPORTANT part of this tool
    """
    # TODO: Implement this tool WITH a human-in-the-loop approval gate
    # Steps:
    #   1. FIRST: Return a confirmation prompt (don't make changes yet!)
    #      - List all IPs that will be deprecated
    #      - Show the current status of each IP
    #      - Ask the user to confirm
    #   2. AFTER CONFIRMATION: Execute the changes
    #      - For each IP, call netbox.get_ip_details() to get the object ID
    #      - Call netbox.deprecate_ip(ip_id) to change status to Deprecated
    #      - Collect results and return summary
    #   3. Handle errors: If an IP doesn't exist or can't be changed, report it
    #
    # HINT for HITL pattern:
    #   You could add a `confirmed: bool = False` parameter. On the first call
    #   (confirmed=False), return the confirmation prompt. On the second call
    #   (confirmed=True), execute the changes. The AI agent handles the user
    #   interaction between the two calls.
    raise NotImplementedError("TODO: Implement execute_reclamation with HITL gate")


# ============================================================================
# Server entry point
# ============================================================================


def main() -> None:
    """Start the Reclaim Agent MCP server.

    This function is called when you run:
        uv run reclaim-agent

    It starts the MCP server using stdio transport, which means it
    communicates with the AI agent via stdin/stdout.
    """
    logger.info("Starting Reclaim Agent MCP server...")
    logger.info("NetBox URL: %s", settings.NETBOX_URL)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
