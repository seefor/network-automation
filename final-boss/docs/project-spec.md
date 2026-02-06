# Final Boss: Operation Reclaim

## The Autonomous IP Address Reclamation Agent

### Project Overview

Every enterprise network accumulates stale IP address allocations over time.
Servers get decommissioned, VMs get deleted, test environments get torn down --
but the IP addresses remain "active" in the source of truth (NetBox). Over
months and years, this drift between what is allocated and what is actually in
use wastes address space, causes confusion during troubleshooting, and creates
security blind spots.

Your mission is to build an **AI-powered reclamation agent** that:

1. Queries NetBox to discover allocated IP addresses
2. Polls live network devices (via SSH) to check which IPs are actually in use
3. Cross-references the two to identify stale addresses
4. Generates a human-readable reclamation report
5. Executes reclamation (marking stale IPs as deprecated) -- but ONLY after
   a human operator explicitly approves

You will build this as an **MCP server** that exposes tools to an AI model.
The AI handles the conversation, decides which tools to call and in what order,
and manages the interaction with the human operator. You write the tools.

This project ties together everything from the course: REST APIs (Milestone 1),
AI-assisted development (Milestone 2), and MCP tool design (Milestone 3).

---

## Architecture

```
+---------------------------------------------------------------------+
|                         HUMAN OPERATOR                               |
|                    (Claude Desktop or Streamlit UI)                   |
+----------------------------------+----------------------------------+
                                   |
                          Natural Language
                                   |
                                   v
+----------------------------------+----------------------------------+
|                   AI MODEL (Claude or Ollama)                        |
|                                                                      |
|  Receives user requests, decides which tools to call, interprets     |
|  results, generates reports, and asks for confirmation before         |
|  executing write operations.                                         |
+----------------------------------+----------------------------------+
                                   |
                         MCP Protocol (stdio)
                                   |
                                   v
+----------------------------------+----------------------------------+
|                     MCP SERVER (your code)                           |
|                     src/reclaim_agent/server.py                      |
|                                                                      |
|  Exposes 6 tools:                                                    |
|    1. query_netbox_prefixes      4. find_stale_ips                   |
|    2. query_netbox_addresses     5. generate_reclamation_report      |
|    3. poll_device_arp            6. execute_reclamation              |
+-----+-----------------------+-----------------------+---------------+
      |                       |                       |
      v                       v                       v
+------------+        +---------------+       +---------------+
|  NetBox    |        |  Mockit       |       |  Mockit       |
|  (REST)    |        |  switch-01    |       |  switch-02/03 |
|            |        |  (SSH)        |       |  (SSH)        |
| Source of  |        | Emulated      |       | Emulated      |
| Truth      |        | Arista EOS    |       | Arista EOS    |
+------------+        +---------------+       +---------------+
 localhost:8000        172.20.20.11          172.20.20.12/.13
```

---

## Technical Requirements

### Part A: MCP Server Tools

You must implement **six tools** in `src/reclaim_agent/server.py`. Each tool
is a Python function decorated with the MCP `@server.tool()` decorator. The
skeleton file is already wired up -- you fill in the logic.

#### Tool 1: query_netbox_prefixes

| Attribute     | Value |
|---------------|-------|
| **Purpose**   | List IP prefixes from NetBox |
| **Parameters**| `status` (optional): filter by prefix status; `site` (optional): filter by site slug |
| **Returns**   | JSON list of prefixes with prefix, status, VLAN, site, description |
| **API**       | `GET /api/ipam/prefixes/` |
| **Hint**      | Use `httpx` to call the NetBox REST API. Pass the NetBox token in the `Authorization` header. |

#### Tool 2: query_netbox_addresses

| Attribute     | Value |
|---------------|-------|
| **Purpose**   | List individual IP addresses from NetBox |
| **Parameters**| `prefix` (optional): parent prefix to filter by; `status` (optional): filter by address status |
| **Returns**   | JSON list of addresses with address, status, DNS name, description, assigned object |
| **API**       | `GET /api/ipam/ip-addresses/` |
| **Hint**      | The `parent` query parameter filters addresses within a prefix. |

#### Tool 3: poll_device_arp

| Attribute     | Value |
|---------------|-------|
| **Purpose**   | SSH into a network device and retrieve its ARP table |
| **Parameters**| `hostname` (required): device hostname or management IP |
| **Returns**   | JSON list of ARP entries with ip_address, mac_address, interface |
| **Method**    | SSH using `netmiko` (Arista EOS platform) |
| **Command**   | `show arp` (or `show ip arp` depending on platform) |
| **Hint**      | Use `netmiko.ConnectHandler` with `device_type="arista_eos"`. Parse the output using string splitting or TextFSM. Default credentials: `admin` / `admin`. |

#### Tool 4: find_stale_ips

| Attribute     | Value |
|---------------|-------|
| **Purpose**   | Cross-reference NetBox allocations against live ARP data |
| **Parameters**| `prefix` (required): the prefix to analyze; `hostnames` (required): list of device hostnames to poll |
| **Returns**   | JSON object with `stale_ips` (list), `active_ips` (list), `total_allocated`, `total_stale` |
| **Logic**     | 1) Call `query_netbox_addresses` for the prefix. 2) Call `poll_device_arp` for each hostname. 3) An IP is "stale" if it is active in NetBox but NOT in any ARP table. |
| **Hint**      | This tool calls your other tools internally. Use set operations for the comparison. Strip CIDR notation (`/24`) from NetBox addresses before comparing with ARP IPs. |

#### Tool 5: generate_reclamation_report

| Attribute     | Value |
|---------------|-------|
| **Purpose**   | Produce a structured reclamation report |
| **Parameters**| `prefix` (required): the prefix that was analyzed; `stale_ips` (required): list of stale IP addresses |
| **Returns**   | JSON object with report title, timestamp, prefix, list of stale IPs with details, recommended action, and summary statistics |
| **Hint**      | Look up each stale IP in NetBox to include its DNS name and description in the report. Include a timestamp. This is a read-only operation. |

#### Tool 6: execute_reclamation

| Attribute     | Value |
|---------------|-------|
| **Purpose**   | Mark stale IPs as deprecated in NetBox |
| **Parameters**| `ip_addresses` (required): list of IPs to deprecate; `reason` (optional): audit log reason |
| **Returns**   | JSON object with results per IP (success/failure) and summary |
| **API**       | `PATCH /api/ipam/ip-addresses/{id}/` with `{"status": "deprecated"}` |
| **CRITICAL**  | This is a **write operation**. The AI must ask for human confirmation before calling this tool. Your tool description must clearly state this requirement. |
| **Hint**      | First look up each IP's NetBox ID, then PATCH the status. Return per-IP success/failure so the operator knows exactly what changed. |

### Part B: AI Conversation Flow

The AI (Claude) drives the conversation. You do NOT write conversation logic --
you design tools so the AI can use them effectively. A successful agent
interaction looks like this:

```
Human: "Check the 10.0.1.0/24 subnet for stale IPs and clean them up."

AI: [calls query_netbox_prefixes to verify the prefix exists]
AI: [calls query_netbox_addresses(prefix="10.0.1.0/24") to see allocations]
AI: [calls poll_device_arp(hostname="172.20.20.11")]
AI: [calls poll_device_arp(hostname="172.20.20.12")]
AI: [calls poll_device_arp(hostname="172.20.20.13")]
AI: [calls find_stale_ips(prefix="10.0.1.0/24", hostnames=[...])]
AI: "I found 3 stale IPs in 10.0.1.0/24. Here is the reclamation report:"
AI: [calls generate_reclamation_report(...)]
AI: "Would you like me to proceed with reclamation? This will mark
     these 3 addresses as deprecated in NetBox."