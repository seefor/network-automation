# Milestone 2: The "Co-Pilot" Era

Use LLMs as coding assistants to accelerate network automation development.
By the end of this milestone you will know how to write effective prompts,
generate network scripts with AI assistance, and critically evaluate AI output
for correctness and safety.

## Prerequisites

- Completed [Milestone 1](../milestone-1-manual/) (REST APIs, Python basics)
- Python 3.11+
- Access to an LLM (Claude, ChatGPT, or a local model)
- A running Containerlab topology with 3 Arista cEOS switches
- `pip install netmiko pyyaml rich`

## Lessons

| # | Lesson | Description |
|---|--------|-------------|
| 1 | [LLM Basics for Network Engineers](lessons/01-llm-basics-for-neteng.md) | What LLMs are, how they work, and why you should care |
| 2 | [Prompt Engineering (P.E.N.E.)](lessons/02-prompt-engineering.md) | Structured prompts, role assignment, few-shot examples |
| 3 | [AI-Assisted Scripting](lessons/03-ai-assisted-scripting.md) | Generate, review, and debug network scripts with AI |

## Labs

| # | Lab | Description |
|---|-----|-------------|
| 1 | [Prompt Crafting](labs/lab01_prompt_crafting.md) | Write prompts that produce working network automation scripts |
| 2 | [Device Audit Script](labs/lab02_audit_script.py) | Complete a skeleton audit script with AI assistance |

## Inventory

The labs use a shared [inventory.yml](labs/inventory.yml) targeting 3 Arista
cEOS switches in a Containerlab topology.

Solutions are in the [solutions/](solutions/) directory. Try the labs yourself
before looking.

## Key Concepts

- **P.E.N.E.**: Prompt Engineering for Network Engineers
- **Tokens**: The units LLMs use to process text (~4 characters per token)
- **Context Window**: The total input + output an LLM can handle in one request
- **Few-Shot Prompting**: Giving the LLM examples of desired input/output pairs
- **Chain-of-Thought**: Asking the LLM to reason step-by-step before answering
- **Hallucination**: When an LLM generates plausible but incorrect output
