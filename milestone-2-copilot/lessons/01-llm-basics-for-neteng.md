# Lesson 1: LLM Basics for Network Engineers

## What Is an LLM?

A Large Language Model (LLM) is a program trained on massive amounts of text.
It predicts the most likely next word given the words before it. That is the
entire trick. There is no database of facts inside it, no search engine, no
reasoning engine -- just a very sophisticated pattern matcher trained on
billions of documents.

Why does this matter to you as a network engineer? Because LLMs have seen
enough code, documentation, RFCs, vendor guides, and Stack Overflow answers
that they can generate useful network automation code, explain protocols, and
help debug configurations. They are not infallible. They are not a replacement
for knowing your craft. But they are a powerful accelerator when used correctly.

## Core Concepts

### Tokens

LLMs do not read characters or words. They read **tokens** -- chunks of text
that average about 4 characters each.

```
"show ip interface brief" = ["show", " ip", " interface", " brief"]  (4 tokens)
"192.168.1.0/24"          = ["192", ".", "168", ".", "1", ".", "0", "/", "24"]  (9 tokens)
```

Why care? Because you pay per token, and the model's context window is measured
in tokens. Long CLI outputs burn through your budget fast.

**Practical rule:** A typical Cisco `show run` on a production switch is
2,000-5,000 tokens. Pasting three of those into a prompt eats 6,000-15,000
tokens before the model even starts answering.

### Context Window

The context window is the total number of tokens the model can handle in a
single request (input + output combined).

| Model | Context Window | Runs Locally |
|-------|---------------|-------------|
| Llama 3.1 (8B) | 128K tokens | Yes (Ollama) |
| Llama 3.1 (70B) | 128K tokens | Yes (needs 48GB+ RAM) |
| Mistral (7B) | 32K tokens | Yes (Ollama) |
| Qwen 2.5 (7B) | 128K tokens | Yes (Ollama) |

Bigger is not always better. Models tend to lose track of details in the
middle of very long contexts (the "lost in the middle" problem). For network
automation, keep your prompts focused:

- Send one device's config, not twenty.
- Ask one question per prompt when precision matters.
- Summarize the problem before pasting raw output.

### Temperature

Temperature controls randomness in the model's output.

| Temperature | Behavior | Use Case |
|-------------|----------|----------|
| 0.0 | Deterministic, picks the most likely token every time | Code generation, config parsing |
| 0.3-0.5 | Slight variation, still mostly predictable | Technical writing, explanations |
| 0.7-1.0 | Creative, more varied output | Brainstorming, generating alternatives |

**For network automation, use temperature 0.** You want the same correct
answer every time, not creative variations on a BGP config.

### System Prompts

A system prompt is an instruction you give the model before your actual
question. It sets the model's behavior for the entire conversation.

```
System: You are a senior network engineer specializing in Arista EOS
and data center fabrics. When asked to generate configurations, always
include comments explaining each section. Output configs in CLI format,
not JSON.
```

Think of it as setting the model's "role" before the conversation begins. A
well-written system prompt eliminates repetition -- you do not need to say
"you are a network engineer" in every message.

## What LLMs Are Good At (For Network Engineers)

1. **Generating boilerplate code** -- Netmiko connection handlers, Jinja2
   templates, YAML schemas. The boring stuff you have written a hundred times.

2. **Translating between formats** -- "Convert this Cisco IOS config to
   Arista EOS" or "Turn this JSON API response into a Markdown table."

3. **Explaining errors** -- Paste a traceback or syslog message, ask what it
   means.

4. **Reviewing configurations** -- "Does this BGP config have any obvious
   problems?"

5. **Writing documentation** -- Docstrings, README files, inline comments.

## What LLMs Are Bad At

1. **Real-time network state** -- The model does not have access to your
   network. It cannot ping a device or check if an interface is up.

2. **Exact syntax for niche vendors** -- Training data skews toward Cisco,
   Arista, and Juniper. Obscure vendor CLIs may produce hallucinated commands.

3. **Math-heavy tasks** -- Subnet calculations, ECMP hash distributions.
   Use a calculator or Python, not an LLM.

4. **Security-critical decisions** -- Never blindly apply AI-generated ACLs
   or firewall rules to production without review.

5. **Remembering previous conversations** -- Each new API call starts fresh
   unless you explicitly send conversation history.

## The Mental Model

Think of an LLM as a **very well-read junior engineer** who has studied every
vendor doc, RFC, and blog post ever published -- but has never actually touched
a live network. They can write you a great first draft. They can explain
concepts clearly. But you always review their work before pushing to
production.

## Running Models Locally with Ollama

This course uses **Ollama** to run LLMs entirely on your machine -- no API
keys, no cloud dependencies. Ollama manages model downloads and serves them
via a local API that our tools call automatically.

To get started:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the recommended model
ollama pull llama3.1

# Start the server
ollama serve
```

See the full [Ollama Setup Guide](../../final-boss/docs/ollama-setup.md) for
detailed installation, model recommendations, GPU acceleration, and
troubleshooting.

## Next Steps

Now that you understand what LLMs are and are not, the next lesson covers how
to write effective prompts -- the single most important skill for getting
useful output from any model.

[Next: Prompt Engineering for Network Engineers ->](02-prompt-engineering.md)
