# Lab 1: Prompt Crafting

## Objective

Write prompts that produce working network automation scripts. Each challenge
asks you to craft a prompt using the P.E.N.E. framework, submit it to an LLM,
and evaluate the result.

## Setup

- Access to an LLM (Claude, ChatGPT, or a local model)
- Your Containerlab topology running 3 Arista cEOS switches
- The [inventory.yml](inventory.yml) file from this directory
- Python 3.11+ with `netmiko`, `pyyaml`, and `rich` installed

## Rules

1. You write the **prompt**, not the code. The LLM writes the code.
2. Use the P.E.N.E. framework: Role, Context, Task, Format, Guardrails.
3. You may refine your prompt iteratively (most challenges will take 2-3 rounds).
4. After the LLM generates code, you must **test it** against your lab switches.
5. Record your final prompt and any refinements you made.

---

## Challenge 1: NTP Audit (Beginner)

**Goal:** Write a prompt that generates a Python script to check NTP
synchronization status across all switches in your inventory.

**Requirements the generated script must meet:**
- Load devices from `inventory.yml`
- Connect via Netmiko
- Run `show ntp status` on each device
- Print whether each device is synchronized and its stratum
- Handle connection failures gracefully

**Hints:**
- Specify the vendor (Arista EOS) and library (Netmiko) in your prompt.
- Ask for type hints and error handling explicitly.

**Evaluation:**
- [ ] Script runs without errors
- [ ] Correctly reports NTP sync status for all 3 switches
- [ ] Does not crash if a device is unreachable

---

## Challenge 2: Interface Report (Beginner)

**Goal:** Write a prompt that generates a script to produce a formatted report
of all interfaces and their status.

**Requirements the generated script must meet:**
- Run `show interfaces status` on each device
- Parse the output into structured data
- Display results in a `rich` table with columns: Device, Interface, Status,
  VLAN, Speed, Type
- Color-code rows: green for "connected", red for "notconnect"

**Hints:**
- Include a sample line of `show interfaces status` output in your prompt
  as a few-shot example so the LLM knows the exact format to parse.

**Evaluation:**
- [ ] Table renders correctly with `rich`
- [ ] All interfaces from all devices appear
- [ ] Color coding works as specified

---

## Challenge 3: SNMP Community String Audit (Intermediate)

**Goal:** Write a prompt that generates a script to audit SNMP community
strings and flag any using default or weak values.

**Requirements the generated script must meet:**
- Run `show running-config section snmp` on each device
- Parse out all configured community strings
- Compare against a list of known-bad values: `public`, `private`, `community`,
  `test`, `default`
- Output a report showing: Device, Community String, Status (OK/FLAGGED)
- Exit with return code 1 if any flagged strings are found (useful for CI/CD)

**Hints:**
- This is a good place to use guardrails in your prompt: "never print the
  actual community string value in the FLAGGED output, just print asterisks."
- Specify that the script should work as a CI check with exit codes.

**Evaluation:**
- [ ] Correctly identifies all SNMP community strings
- [ ] Flags known-bad values
- [ ] Exits with code 1 on failure, 0 on success
- [ ] Does not leak community string values in output

---

## Challenge 4: Config Backup With Diff (Intermediate)

**Goal:** Write a prompt that generates a script to back up running configs
and compare them against a known-good baseline.

**Requirements the generated script must meet:**
- Run `show running-config` on each device
- Save each config to a file named `{hostname}_{date}.cfg`
- If a previous backup exists, show a unified diff between old and new
- Summarize changes: lines added, lines removed, total diff lines
- Use `pathlib` for file operations, not `os.path`

**Hints:**
- Ask the LLM to use Python's built-in `difflib` module.
- Specify the date format for filenames (e.g., `2024-01-15`).
- Tell the model where to store backups (e.g., a `backups/` directory).

**Evaluation:**
- [ ] Configs are saved with correct filenames
- [ ] Diff output is readable and correct
- [ ] Summary counts match the actual diff
- [ ] Script creates the backup directory if it does not exist

---

## Challenge 5: Multi-Check Compliance Report (Advanced)

**Goal:** Write a prompt that generates a comprehensive compliance audit
script checking multiple best practices in a single run.

**Requirements the generated script must meet:**
- Check all of the following on each device:
  - NTP: at least one NTP server configured
  - DNS: at least one name-server configured
  - SNMP: no default community strings (`public`/`private`)
  - Syslog: at least one logging host configured
  - AAA: authentication configured (not just local)
  - Banner: a login banner is present
- Output a compliance matrix: rows = devices, columns = checks,
  cells = PASS/FAIL
- Use `rich` for the table with color coding (green PASS, red FAIL)
- Generate a JSON report file alongside the console output
- Accept an `--inventory` CLI flag to specify the inventory file path

**Hints:**
- This is complex. Use iterative refinement: first get the structure right,
  then add checks one at a time.
- Specify the exact commands to run for each check so the LLM does not
  guess wrong.
- Ask for a `Check` dataclass or similar structure to keep the code clean.

**Evaluation:**
- [ ] All six checks work correctly
- [ ] Table displays properly with color coding
- [ ] JSON report is valid and contains all results
- [ ] Script accepts `--inventory` CLI argument
- [ ] Handles device connection failures without crashing

---

## Submission

For each challenge, save:
1. Your final prompt (in a text file or as a comment in the generated script)
2. The generated script
3. A screenshot or log of the script running against your lab

## Reflection Questions

After completing the challenges, answer these:

1. How many prompt iterations did each challenge take? Which required the most
   refinement and why?
2. Did the LLM generate any incorrect CLI commands? How did you catch them?
3. What was the most effective prompting technique you used?
4. Where did you have to manually edit the AI-generated code? What patterns
   do you notice in what the AI gets wrong?
