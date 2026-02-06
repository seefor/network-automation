# Lesson 2: Prompt Engineering for Network Engineers (P.E.N.E.)

## Why Prompts Matter

The difference between "write me a Python script" and a well-structured prompt
is the difference between getting a generic toy and getting a production-ready
tool. Prompt engineering is not about tricking the model. It is about
communicating clearly -- the same skill that makes you good at writing runbooks
and change requests.

## The P.E.N.E. Framework

A structured prompt for network automation has five parts:

```
1. ROLE       - Who the model should act as
2. CONTEXT    - What the model needs to know about your environment
3. TASK       - What you want done (be specific)
4. FORMAT     - How the output should look
5. GUARDRAILS - What to avoid or validate
```

### Example: The Full Framework

```
ROLE: You are a senior network automation engineer who writes production
Python code for Arista EOS environments.

CONTEXT: I manage 3 Arista EOS switches in a lab on the management
network 172.20.20.0/24. They are reachable via SSH.
I use Netmiko for device access and YAML for inventory files.

TASK: Write a Python script that connects to each switch, runs
"show ntp status" and "show ntp associations", then reports whether
NTP is synchronized and what the stratum is.

FORMAT: Output a Python script with type hints. Use a dataclass for
results. Print a summary table at the end using the rich library.

GUARDRAILS: Do not use global variables. Handle connection timeouts
gracefully. Do not hardcode credentials -- read them from environment
variables.
```

## Technique 1: Role Assignment

Setting a role is not fluff. It changes the model's output distribution.

| Role | Effect |
|------|--------|
| "You are a network engineer" | Generic networking knowledge |
| "You are a senior Arista TAC engineer" | Arista-specific syntax, EOS idioms |
| "You are a Python developer who writes network automation" | Better code structure, proper error handling |
| "You are a security auditor reviewing firewall rules" | Focuses on risks, gaps, best practices |

**Pick the role that matches the expertise you need.**

## Technique 2: Output Formatting

Tell the model exactly what format you want. Otherwise you get whatever it
feels like generating.

```
Bad:  "Show me the BGP neighbors"
Good: "Output BGP neighbor information as a Markdown table with columns:
       Neighbor IP, ASN, State, Prefixes Received, Uptime"
```

Common format directives for network work:

- `"Output as a Python script with type hints"`
- `"Output as a Jinja2 template"`
- `"Output as a YAML file"`
- `"Output as CLI commands I can paste into an Arista switch"`
- `"Output as a Markdown table"`
- `"Output as a JSON object matching this schema: {...}"`

## Technique 3: Few-Shot Examples

Few-shot prompting means giving the model examples of the input/output pattern
you want before asking your actual question.

```
I need to parse Arista EOS "show interfaces status" output into
structured data. Here are two examples:

Input:
Et1       connected  Vlan10    full    1000    1000BASE-T

Output:
{"interface": "Ethernet1", "status": "connected", "vlan": "10",
 "duplex": "full", "speed": "1000", "type": "1000BASE-T"}

Input:
Et2       notconnect Vlan20    auto    auto    Not Present

Output:
{"interface": "Ethernet2", "status": "notconnect", "vlan": "20",
 "duplex": "auto", "speed": "auto", "type": "Not Present"}

Now parse this:
Et3       connected  Vlan30    full    10G     10GBASE-SR
```

Few-shot is especially useful for:
- Parsing non-standard CLI output
- Converting between vendor config formats
- Generating consistent YAML/JSON schemas

## Technique 4: Chain-of-Thought for Troubleshooting

When using an LLM to help troubleshoot, ask it to reason step by step.
This reduces hallucination and produces more accurate diagnoses.

```
A user reports they cannot reach 10.1.1.100 from VLAN 20.

Think through this step by step:
1. What layer should we check first?
2. What commands would you run on the switch?
3. For each possible result, what would it tell us?
4. What is the most likely root cause?

Do not jump to conclusions. Show your reasoning.
```

The key phrase is **"think step by step"** or **"show your reasoning."**
Without it, the model tends to jump to the most statistically common answer,
which may not match your specific situation.

## Technique 5: Iterative Refinement

Do not try to write the perfect prompt on the first attempt. Work in rounds:

```
Round 1: "Write a script to check NTP on my switches"
         -> Output is okay but uses hardcoded IPs

Round 2: "Good, but load device list from a YAML inventory file
          instead of hardcoding IPs"
         -> Better, but no error handling

Round 3: "Add try/except blocks for SSH connection failures and
          print which devices failed"
         -> Now it is production-worthy
```

Each round narrows the gap between what you got and what you need. This is
faster than trying to specify everything upfront.

## Real Networking Prompt Examples

### Prompt 1: Config Generation

```
ROLE: Senior Arista network engineer.

TASK: Generate an Arista EOS configuration snippet that:
- Creates VLAN 100 named "SERVERS"
- Assigns IP 10.100.0.1/24 to interface Vlan100
- Enables OSPF area 0 on that interface
- Sets the OSPF cost to 10

FORMAT: Output as EOS CLI commands I can paste directly.
Include comments above each section.
```

### Prompt 2: Script Generation

```
ROLE: Python network automation developer.

CONTEXT: I use Netmiko to connect to Arista EOS switches. Devices are
listed in a YAML file with fields: hostname, ip, username, password.

TASK: Write a Python script that:
1. Loads the YAML inventory
2. Connects to each device via SSH
3. Runs "show ip bgp summary"
4. Parses the output to extract neighbor IP, state, and prefixes received
5. Prints a summary table

FORMAT: Python 3.11+ with type hints. Use dataclasses. Use the rich
library for table output.

GUARDRAILS: Handle connection failures per-device (do not crash if one
device is unreachable). Read SSH credentials from environment variables.
```

### Prompt 3: Troubleshooting

```
ROLE: Senior network engineer specializing in BGP.

CONTEXT: I have two Arista switches in an eBGP peering. Here is the
relevant config and status output from both sides:

[paste configs and "show ip bgp summary" from both switches]

TASK: Analyze why the BGP session is stuck in "Active" state.

Think step by step:
1. Check if the peering IPs are correct on both sides
2. Check if the ASN numbers match expectations
3. Check if there are any route-map or prefix-list filters blocking
4. Check for any MTU or TCP connectivity issues
5. Provide the most likely root cause and fix

FORMAT: Numbered list of findings, then a recommended fix as CLI commands.
```

### Prompt 4: Config Review

```
ROLE: Network security auditor.

TASK: Review this switch configuration for security best practices.
Check for:
- Default credentials or weak authentication
- Missing control plane protection (CoPP)
- Open management protocols (telnet, HTTP)
- Missing NTP authentication
- SNMP v2c with default community strings

[paste configuration]

FORMAT: Markdown table with columns: Finding, Severity (High/Medium/Low),
Recommendation. Sort by severity descending.
```

### Prompt 5: Format Conversion

```
ROLE: Network automation engineer.

TASK: Convert this Cisco IOS interface configuration to Arista EOS syntax.

Input:
interface GigabitEthernet0/1
 description Uplink to Core
 ip address 10.0.0.1 255.255.255.252
 ip ospf 1 area 0
 ip ospf cost 100
 speed 1000
 duplex full
 no shutdown

FORMAT: Output the equivalent Arista EOS CLI commands. Add a comment
above any lines where the syntax differs from IOS explaining what changed.
```

### Prompt 6: Documentation Generation

```
ROLE: Technical writer for a network engineering team.

CONTEXT: Here is the Python script our team uses to audit SNMP
configurations across our switches:

[paste script]

TASK: Write a docstring for the main function and inline comments for
any non-obvious logic. Also generate a one-paragraph summary I can put
in our team wiki.

FORMAT: Return the complete script with comments added. Put the wiki
summary at the top as a block comment.
```

## Anti-Patterns (What Not to Do)

| Anti-Pattern | Why It Fails | Fix |
|-------------|-------------|-----|
| "Write me a network script" | Too vague, model guesses everything | Specify vendor, library, devices, and task |
| Pasting 10 configs at once | Exceeds useful context, model loses detail | One device per prompt or summarize first |
| "Make it perfect" | Not actionable | Specify what "perfect" means: error handling, logging, tests |
| No format specified | Model picks whatever format it wants | Always specify: Python, CLI, YAML, table, etc. |
| Trusting output blindly | LLMs hallucinate CLI commands | Always test on a lab device first |

## Next Steps

You can write effective prompts. Next, we put this to work: using AI to
generate, review, and debug real network automation scripts.

[Next: AI-Assisted Scripting ->](03-ai-assisted-scripting.md)
