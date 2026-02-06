# Shared Lab Infrastructure

This directory contains the Docker configurations and scripts that power
the course lab environment.

## Directory Structure

```
shared/
├── docker/
│   ├── docker-compose.yml         # NetBox + mock switches stack
│   └── mockit/                    # Per-switch command templates
│       ├── switch-01/templates/   # ARP table, interfaces, version
│       ├── switch-02/templates/
│       └── switch-03/templates/
└── scripts/
    └── seed_netbox.py             # Populates NetBox with lab data
```

## NetBox Stack

The lab uses **NetBox v3.7** (explicitly pinned for stable API token support).

| Container | Purpose | Access |
|-----------|---------|--------|
| `netbox` | NetBox web UI + API | http://localhost:8000 |
| `netbox-postgres` | PostgreSQL 16 database | internal |
| `netbox-redis` | Redis cache + task queue | internal |

### Why v3.7?

NetBox 4.0 changed its API token format from v1 to v2. The `SUPERUSER_API_TOKEN`
environment variable creates a v1-format token, which NetBox 4.0 rejects with
"Invalid v1 token". Pinning to v3.7 ensures the pre-configured token works
out of the box.

### Default Credentials

| Resource | Value |
|----------|-------|
| Web UI login | `admin` / `admin` |
| API Token | `0123456789abcdef0123456789abcdef01234567` |
| PostgreSQL | `netbox` / `netbox_db_password` |

## Mock Network Switches (Mockit)

The lab uses [Mockit](https://gitlab.com/slurpit.io/mockit) to emulate three
Arista EOS switches. Mockit is a Docker-based network device emulator that
accepts SSH connections and returns pre-configured command output.

Unlike Containerlab, Mockit **runs natively on macOS, Linux, and Windows** —
no Linux VM or special privileges required.

| Container | SSH Access | Role |
|-----------|-----------|------|
| `switch-01` | localhost:2201 | 3 live ARP entries (10.0.1.10-12) |
| `switch-02` | localhost:2202 | 2 live ARP entries (10.0.1.20-21) |
| `switch-03` | localhost:2203 | 1 live ARP entry (10.0.1.30) |

### How It Works

Each switch has template files in `mockit/<switch>/templates/` that define
what commands return. The filename matches the exact command:

```
mockit/switch-01/templates/
├── show ip arp              # Returns ARP table with live IPs
├── show ip interface brief  # Returns interface summary
├── show version             # Returns device info
└── show hostname            # Returns device hostname
```

When a Netmiko script runs `show ip arp` against switch-01, Mockit returns
the contents of the `show ip arp` file — which contains only the "live"
IPs (10.0.1.10, .11, .12). The stale IPs (10.0.1.50-52, .100-.101) exist
only in NetBox, so the reclamation agent correctly identifies them as stale.

### SSH Credentials

All switches use `admin` / `admin` (configured via `SSH_USERNAME` and
`SSH_PASSWORD` environment variables in docker-compose.yml).

### Starting the Stack

```bash
# From the repo root — starts everything (NetBox + switches + seed data)
make lab-up

# Or manually
docker compose -f shared/docker/docker-compose.yml up -d
uv run python shared/scripts/seed_netbox.py
```

## Seed Data

The `seed_netbox.py` script creates:

- **Site:** Lab
- **Manufacturer:** Arista
- **Device Type:** cEOS
- **Devices:** switch-01, switch-02, switch-03
- **Prefixes:** Management, server subnet, point-to-point links
- **IP Addresses:** Mix of "live" (have ARP entries) and "stale" (NetBox-only)

The stale IPs (10.0.1.50-52, 10.0.1.100-101) are intentionally created for
the Final Boss reclamation agent to discover.

## Troubleshooting

### NetBox not responding on port 8000

```bash
# Check container status
docker compose -f shared/docker/docker-compose.yml ps

# View logs
docker logs netbox
```

### API returns 403 Forbidden

Verify the token is correct:

```bash
curl -H "Authorization: Token 0123456789abcdef0123456789abcdef01234567" \
     http://localhost:8000/api/dcim/sites/
```

If still failing, the NetBox database may need to be recreated:

```bash
docker compose -f shared/docker/docker-compose.yml down -v
make lab-up
```

### Cannot SSH to mock switches

Verify the switch containers are running:

```bash
docker ps --filter "name=switch"
```

Test SSH connectivity via Netmiko:

```python
from netmiko import ConnectHandler
conn = ConnectHandler(
    device_type="arista_eos",
    host="localhost",
    port=2201,
    username="admin",
    password="admin",
)
print(conn.send_command("show ip arp"))
conn.disconnect()
```
