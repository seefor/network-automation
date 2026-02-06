# Configuring Claude Desktop with the Reclaim Agent MCP Server

This guide walks you through connecting Claude Desktop to the Final Boss
MCP server so Claude can query NetBox, poll network devices, and execute
IP reclamation on your behalf.

## Prerequisites

- Claude Desktop installed ([download](https://claude.ai/download))
- `uv` installed and on your PATH
- The `reclaim-agent` package installable (run `uv pip install -e .` in
  the `final-boss/` directory to verify)
- Lab environment running (`make lab-up` from the repo root)

## Step 1: Locate the Claude Desktop Config File

Claude Desktop stores its MCP server configuration in a JSON file. The
location depends on your operating system:

| OS      | Config file path                                                         |
|---------|--------------------------------------------------------------------------|
| macOS   | `~/Library/Application Support/Claude/claude_desktop_config.json`        |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json`                            |
| Linux   | `~/.config/Claude/claude_desktop_config.json`                            |

If the file does not exist, create it. If it already exists and has other
server entries, you will add a new entry to the `mcpServers` object.

**Quick open (macOS):**

```bash
# Open the directory in Finder
open ~/Library/Application\ Support/Claude/

# Or edit directly
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Quick open (Windows PowerShell):**

```powershell
code "$env:APPDATA\Claude\claude_desktop_config.json"
```

## Step 2: Add the Server Entry

Copy the following into your `claude_desktop_config.json`. If the file
already has a `mcpServers` object, add the `reclaim-agent` key to it.

```json
{
  "mcpServers": {
    "reclaim-agent": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/ABSOLUTE/PATH/TO/network-automation/final-boss",
        "reclaim-agent"
      ],
      "env": {
        "NETBOX_URL": "http://localhost:8000",
        "NETBOX_TOKEN": "your-netbox-api-token-here"
      }
    }
  }
}
```

### Field reference

| Field       | Description                                                                                  |
|-------------|----------------------------------------------------------------------------------------------|
| `command`   | The executable to run. We use `uv` so it handles the virtual environment automatically.      |
| `args`      | Arguments passed to `uv`. `--directory` tells uv where the project lives. `reclaim-agent` is the console script entry point defined in `pyproject.toml`. |
| `env`       | Environment variables passed to the server process. Set your NetBox URL and API token here.   |

### Important: Update the path

Replace `/ABSOLUTE/PATH/TO/network-automation/final-boss` with the actual
absolute path on your machine. For example:

```
macOS:   /Users/yourname/work/network-automation/final-boss
Windows: C:\\Users\\yourname\\work\\network-automation\\final-boss
Linux:   /home/yourname/work/network-automation/final-boss
```

Do NOT use `~` or `$HOME` -- Claude Desktop requires an absolute path.

### Important: Set your NetBox token

Replace `your-netbox-api-token-here` with the actual API token from your
NetBox instance. You can find (or create) a token at:

```
http://localhost:8000/users/tokens/
```

The default superuser for the lab is `admin` / `admin`.

## Step 3: Restart Claude Desktop

After saving the config file, **quit and relaunch** Claude Desktop. It
reads the config file on startup.

## Step 4: Verify the Connection

1. Open a new conversation in Claude Desktop.
2. Look for the hammer icon (tools) in the input area -- it should show
   a number indicating how many tools are available.
3. Click the hammer icon to see the list of tools. You should see:
   - `query_netbox_prefixes`
   - `query_netbox_addresses`
   - `poll_device_arp`
   - `find_stale_ips`
   - `generate_reclamation_report`
   - `execute_reclamation`
4. Type a test query:

   > What IP prefixes are configured in NetBox?

   Claude should call the `query_netbox_prefixes` tool and display the
   results.

## Troubleshooting

### Tools do not appear (no hammer icon)

- **Check the config path.** The file must be in the exact location for
  your OS (see Step 1). A common mistake is placing it in the wrong
  directory.
- **Check JSON syntax.** Use a JSON validator. A trailing comma or
  missing quote will cause silent failure.
- **Check the absolute path.** The `--directory` arg must be an absolute
  path to the `final-boss/` directory. No `~`, no `$HOME`, no relative
  paths.
- **Restart Claude Desktop.** Config changes require a full restart (quit
  and relaunch, not just close the window).

### Tools appear but calls fail

- **Is the lab running?** Run `make lab-status` from the repo root to
  check that NetBox and the mock switches are up.
- **Is the NetBox token correct?** Try the token in curl:
  ```bash
  curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/ipam/prefixes/
  ```
- **Is `uv` on your PATH?** Claude Desktop uses your system PATH. If
  you installed `uv` in a non-standard location, provide the full path
  in the `command` field (e.g., `/Users/you/.cargo/bin/uv`).
- **Check the MCP server logs.** Run the server manually to see errors:
  ```bash
  cd final-boss
  uv run reclaim-agent
  ```

### "Permission denied" or SSH errors for poll_device_arp

- The mock switches are accessible via localhost port mapping:
  - switch-01: localhost:2201
  - switch-02: localhost:2202
  - switch-03: localhost:2203
- Default credentials: `admin` / `admin`.
- Test SSH access via Netmiko:
  ```python
  from netmiko import ConnectHandler
  conn = ConnectHandler(device_type="arista_eos", host="localhost",
                        port=2201, username="admin", password="admin")
  print(conn.send_command("show ip arp"))
  ```

### Claude says it cannot use a tool

- Verify the tool list matches between your MCP server (`server.py`)
  and what Claude Desktop shows. If you renamed a tool, update both.
- Check that the tool handler does not raise an unhandled exception.
  Claude sees tool errors as failures and may stop trying.

## Alternative: Streamlit UI

If you prefer not to use Claude Desktop, the course includes a Streamlit
chat interface that acts as an MCP client. Run it with:

```bash
make boss-streamlit
# or directly:
cd final-boss && uv run streamlit run src/reclaim_agent/ui.py
```

The Streamlit UI uses Ollama for local inference — no API key required.
See the [Ollama Setup Guide](ollama-setup.md) for installation and
configuration instructions.
