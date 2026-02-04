# Lesson 3: AI-Assisted Scripting

## The Workflow

Using AI to write network scripts is not "type a prompt and ship it." It is a
loop:

```
1. Draft a prompt using P.E.N.E.
2. Get the generated code
3. Read every line (yes, every line)
4. Test on a lab device
5. Refine the prompt or edit the code manually
6. Repeat until correct
```

This is faster than writing from scratch, but it is not zero effort. The value
is in skipping boilerplate and getting a working structure in seconds instead
of minutes.

## Generating Scripts

### Start With Structure, Not Details

A good first prompt asks for the skeleton:

```
Write a Python script that connects to Arista switches via Netmiko,
runs a list of show commands, and saves the output to files.

Requirements:
- Load devices from a YAML inventory
- Use type hints and dataclasses
- Include a main() function
- Handle connection errors per device
- Use argparse for CLI options

Do not implement the parsing logic yet. Just get the structure right.
```

Once the structure is solid, follow up with specifics:

```
Now add a function that parses "show ntp status" output and returns
a dataclass with fields: synchronized (bool), stratum (int),
reference_server (str).
```

### Why This Works Better Than One Big Prompt

- You can review and course-correct at each step.
- The model has your approved code as context for the next round.
- You catch structural problems before investing in detail.

## Reviewing AI-Generated Code

Every line of AI-generated code must pass your review. Here is a checklist
for network automation scripts:

### Connection Handling

- [ ] Does it use environment variables or a secrets manager for credentials?
- [ ] Does it set a reasonable connection timeout?
- [ ] Does it handle `NetmikoTimeoutException` and `NetmikoAuthenticationException`?
- [ ] Does it close connections in a `finally` block or use a context manager?

### Command Execution

- [ ] Are the CLI commands correct for your vendor and OS version?
- [ ] Does it use `send_command()` for show commands (not `send_config_set()`)?
- [ ] Does it use `send_config_set()` for config changes (not `send_command()`)?
- [ ] Is `enable()` called when needed for privilege escalation?

### Output Parsing

- [ ] Does the regex or parser handle edge cases (empty output, errors)?
- [ ] Are parsed values the correct type (int vs str, bool vs str)?
- [ ] Does it handle the case where a command returns an error message?

### Safety

- [ ] Does it have a dry-run mode for config changes?
- [ ] Does it log what it is about to do before doing it?
- [ ] Are there no hardcoded credentials anywhere in the file?

## Debugging With AI

When your script fails, AI is excellent at interpreting errors. But you need
to give it context.

### Bad Debugging Prompt

```
My script is broken. Fix it.
```

### Good Debugging Prompt

```
ROLE: Python developer debugging a Netmiko script.

CONTEXT: I am running this script against Arista cEOS in Containerlab.
Python 3.11, Netmiko 4.2, running on macOS.

ERROR: [paste the full traceback]

CODE: [paste the relevant function, not the entire script]

TASK: Explain what is causing this error and provide a fix.
Show the corrected code with comments explaining what changed.
```

### The Rubber Duck Effect

Even when the AI's answer is wrong, the act of structuring your debugging
prompt often helps you spot the issue yourself. You are forced to isolate the
problem, identify the relevant code, and describe what you expected vs. what
happened. That process is debugging.

## When NOT to Trust AI Output

### Hallucinated CLI Commands

LLMs generate text that looks right. For network CLIs, "looks right" can
mean a command that has correct syntax but does not exist on your platform.

Real examples of hallucinated commands:

| Hallucinated Command | Problem |
|---------------------|---------|
| `show ip ospf neighbor detail vrf all` | Valid on NX-OS, not on EOS |
| `ntp authenticate` | Does not exist; correct is `ntp authentication` |
| `ip access-list standard BLOCK permit host 10.0.0.1` | Syntax mash-up of IOS and EOS |
| `set protocols bgp group PEERS peer-as 65001` | Junos-like syntax on an EOS prompt |

**Rule: Never paste AI-generated CLI commands into production without testing
them in a lab first.**

### Invented Library Functions

LLMs sometimes call functions that do not exist in the library version you
are using:

```python
# AI might generate this:
device.get_bgp_neighbors_detail()  # Does not exist in NAPALM

# The real function is:
device.get_bgp_neighbors()
```

**Rule: Check every function call against the library's actual documentation.**

### Confident Nonsense

LLMs do not say "I am not sure." They present everything with the same level
of confidence. A completely wrong subnet calculation and a correct one look
identical in the output.

**Rule: Verify any calculations, IP math, or protocol-specific logic
independently. Use Python's `ipaddress` module, not an LLM, for subnet math.**

### Outdated Information

LLMs have training data cutoffs. If a vendor released a new feature or
deprecated a command after the cutoff, the model does not know about it.

**Rule: For vendor-specific syntax, always cross-reference the current
release notes or CLI guide.**

## Validation Patterns

Build validation into your workflow, not as an afterthought.

### Pattern 1: Lab-First Testing

```
1. AI generates script
2. You review the code
3. Run against Containerlab topology (never production)
4. Compare output to manual CLI verification
5. If output matches, promote to production
```

### Pattern 2: Diff Before Apply

For any script that changes configuration:

```python
def apply_config(device: ConnectHandler, commands: list[str], dry_run: bool = True) -> str:
    """Apply config with mandatory diff check."""
    # Always show what will change first
    device.send_config_set(commands)
    diff: str = device.send_command("show session-config diffs")

    if dry_run:
        device.send_command("abort")
        return f"[DRY RUN] Changes would be:\n{diff}"

    device.send_command("commit")
    return f"Applied:\n{diff}"
```

### Pattern 3: Assert Expected State

After making changes, verify the result:

```python
def verify_ntp(device: ConnectHandler, expected_server: str) -> bool:
    """Verify NTP is configured and pointing at the right server."""
    output: str = device.send_command("show ntp associations")
    return expected_server in output
```

## The Co-Pilot Mindset

You are the pilot. The AI is the co-pilot. It handles the tedious parts --
boilerplate, syntax lookup, first drafts -- while you handle judgment calls:

- Is this the right approach?
- Is this safe for production?
- Does this match our network's actual state?
- Did the AI make something up?

The engineers who get the most value from AI are not the ones who blindly
trust it. They are the ones who use it to move faster while maintaining the
same standard of rigor they always had.

## Next Steps

Time to put these skills into practice. Head to the labs and start writing
prompts that generate real network automation scripts.

[Next: Lab 1 - Prompt Crafting ->](../labs/lab01_prompt_crafting.md)
