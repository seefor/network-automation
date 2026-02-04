# Lesson 03: The Human-in-the-Loop Pattern

## The Rule

**AI must never make network changes without explicit human approval.**

This is not a suggestion. This is not a best practice you can skip in dev. This
is the line between a useful tool and an outage generator.

## Why This Matters

Networks are stateful, fragile, and unforgiving. A bad VLAN assignment doesn't
throw an exception -- it silently black-holes traffic. A wrong route
advertisement doesn't return an error code -- it takes down a region. A misapplied
ACL doesn't log a warning -- it locks you out of the device.

AI models are probabilistic. They are very good at understanding intent, but they
hallucinate, misinterpret, and make confident mistakes. That is fine when the
output is text. It is catastrophic when the output is a config push.

## What Goes Wrong Without HITL

These are real-world failure patterns that happen when automation runs unchecked:

### VLAN Misconfiguration
An AI interprets "move server-12 to the database VLAN" and assigns VLAN 100
instead of VLAN 200. The server loses connectivity to the database tier. The
monitoring system does not alert because the port is still up -- it just cannot
reach anything. A developer notices 45 minutes later when queries start timing
out.

### Route Leak
An AI is asked to "advertise the new prefix to our upstream." It adds a
route-map entry but misses the deny statement at the end. Every internal prefix
is now advertised to the internet. Your ISP starts receiving your /24s. BGP
convergence takes minutes. Traffic is black-holed during reconvergence.

### ACL Lockout
An AI adds a permit statement to an interface ACL but places it after an
implicit deny. Or worse, it replaces the ACL entirely and the new version is
missing the SSH permit line for management access. The device is now unreachable
over the network. Someone drives to the data center with a console cable.

### MTU Mismatch
An AI configures a new link with MTU 9000 (jumbo frames) but the far end is
still at 1500. Large packets are silently dropped. Small pings work. HTTP
requests for small pages work. File transfers fail. This takes hours to
diagnose because "the link is up and ping works."

### Spanning Tree Disaster
An AI reconfigures bridge priorities to "optimize" the spanning tree. It sets a
new root bridge without understanding the existing topology. Every switch
recalculates its forwarding tables simultaneously. The entire Layer 2 domain
goes down for 30-50 seconds. Every phone call drops. Every session resets.

## The Two Categories of Operations

Every network operation falls into one of two categories:

### Read Operations (Safe)
These retrieve information without changing state. They can run freely.

- Show interface status
- Get routing table
- List VLANs
- Query NetBox for device inventory
- Check prefix utilization
- Read running config
- Pull LLDP neighbors

**These are safe for AI to execute autonomously.** The worst case is a wasted
API call.

### Write Operations (Dangerous)
These change network state. They require human approval.

- Push configuration changes
- Modify VLAN assignments
- Update route advertisements
- Change ACL rules
- Modify interface settings
- Create/delete prefixes in IPAM
- Update device records

**These must never execute without a human saying "yes."**

## The Propose-Review-Approve-Execute Workflow

```
+----------+     +----------+     +----------+     +----------+
|          |     |          |     |          |     |          |
| PROPOSE  |---->|  REVIEW  |---->| APPROVE  |---->| EXECUTE  |
|          |     |          |     |          |     |          |
| AI builds|     | Human    |     | Human    |     | System   |
| the plan |     | reads it |     | says yes |     | applies  |
|          |     |          |     | or no    |     | change   |
+----------+     +----------+     +----------+     +----------+
                       |                |
                       |  "This looks   |  "No, change X"
                       |   wrong"       |
                       |                |
                       v                v
                  +----------+     +----------+
                  |          |     |          |
                  |  REJECT  |     |  MODIFY  |
                  |          |     |          |
                  | Abort,   |     | AI revises|
                  | no change|     | the plan  |
                  +----------+     +----------+
```

### Step 1: Propose
The AI analyzes the request and generates a specific plan. Not "I will fix the
VLAN" but "I will set interface Gi0/1 on switch-access-01 to access VLAN 200 with
the following commands:

```
interface GigabitEthernet0/1
  switchport access vlan 200
```

The plan must be concrete, specific, and complete.

### Step 2: Review
The human reads the proposed changes. They can see exactly what will happen,
on which device, with which commands. There is no ambiguity.

### Step 3: Approve or Reject
The human explicitly approves ("yes, execute this") or rejects ("no, that is
wrong because..."). If rejected, the AI goes back to Step 1 with feedback.

### Step 4: Execute
Only after explicit approval does the system apply the change. The execution
is logged with who approved, when, and what was applied.

## Implementing HITL in MCP Servers

In your MCP server, separate read and write tools clearly:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("network-safe")


# READ TOOLS -- These execute immediately
@mcp.tool()
async def get_interface_status(hostname: str, interface: str) -> str:
    """Get interface operational status. Read-only, safe to call anytime."""
    ...


@mcp.tool()
async def get_vlan_list(hostname: str) -> str:
    """List all VLANs configured on a device. Read-only."""
    ...


# WRITE TOOLS -- These propose but do not execute
@mcp.tool()
async def propose_vlan_change(
    hostname: str,
    interface: str,
    vlan_id: int,
) -> str:
    """Propose a VLAN assignment change.

    IMPORTANT: This tool does NOT make changes. It generates a change plan
    that must be reviewed and approved by a human before execution.

    Returns the proposed commands and a change ID for approval.
    """
    commands = [
        f"interface {interface}",
        f"  switchport access vlan {vlan_id}",
    ]
    change_id = "CHG-20240115-001"

    return json.dumps({
        "change_id": change_id,
        "status": "PROPOSED -- AWAITING HUMAN APPROVAL",
        "device": hostname,
        "commands": commands,
        "instructions": "Review the above commands. If correct, approve "
                       "using the approve_change tool with this change_id.",
    })
```

Notice the write tool:
1. Does not execute the change
2. Returns a proposal with specific commands
3. Includes a change ID for tracking
4. Tells the AI (and human) that approval is required

## Naming Conventions

Use tool names that make the safety level obvious:

| Pattern | Meaning | Example |
|---------|---------|---------|
| `get_*` | Read-only | `get_interface_status` |
| `list_*` | Read-only | `list_devices` |
| `show_*` | Read-only | `show_route_table` |
| `check_*` | Read-only | `check_prefix_utilization` |
| `propose_*` | Generates plan, no execution | `propose_config_change` |
| `plan_*` | Generates plan, no execution | `plan_vlan_migration` |
| `approve_*` | Executes a previously proposed change | `approve_change` |

The AI reads these names. Consistent naming helps it understand which tools are
safe and which require caution.

## Tool Descriptions as Guardrails

The tool description is your first line of defense. The AI reads it before
deciding to call the tool. Be explicit:

**Bad:**
```python
@mcp.tool()
async def set_vlan(hostname: str, interface: str, vlan: int) -> str:
    """Set VLAN on an interface."""
```

**Good:**
```python
@mcp.tool()
async def propose_vlan_change(hostname: str, interface: str, vlan: int) -> str:
    """Propose a VLAN assignment change for human review.

    WARNING: This creates a change proposal only. It does NOT apply the change.
    The proposed change must be reviewed and approved by a network engineer
    before execution.

    Returns: A change proposal with the exact commands that would be applied.
    """
```

## Defense in Depth

HITL is one layer. Good automation has multiple:

1. **Tool descriptions** -- Tell the AI what is safe and what is not
2. **Propose-only write tools** -- Write tools generate plans, not changes
3. **Approval gates** -- Separate approve tool requires human confirmation
4. **Audit logging** -- Every tool call is logged with timestamp and parameters
5. **Dry-run mode** -- Test changes against a lab or simulation before production
6. **Rollback plans** -- Every change proposal includes how to undo it

## Key Takeaways

- Read operations are safe for AI to execute freely. Write operations need
  human approval. Always.
- Use the Propose-Review-Approve-Execute workflow for all state changes.
- Name tools clearly: `get_*` for reads, `propose_*` for writes.
- Tool descriptions are guardrails. Write them like safety documentation.
- The AI is your analyst and planner. The human is the approver. The system
  is the executor. Keep these roles separate.
- Networks are unforgiving. A single bad config push can cause an outage that
  takes hours to resolve. The 30 seconds it takes to review a proposal is
  always worth it.

## Next

In Lab 01, you will build your first MCP server with read-only tools and
connect it to Claude Desktop or the Streamlit UI.
