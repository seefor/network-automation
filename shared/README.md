# Shared Lab Infrastructure

This directory contains the Docker and Containerlab configurations that power
the course lab environment.

## Directory Structure

```
shared/
├── docker/
│   ├── docker-compose.yml    # NetBox + PostgreSQL + Redis stack
│   └── topology.clab.yml     # Containerlab topology (Arista cEOS)
└── scripts/
    └── seed_netbox.py        # Populates NetBox with lab data
```

## NetBox Stack

The lab uses **NetBox v3.7** (explicitly pinned for stable API token support).

| Container | Purpose | Port |
|-----------|---------|------|
| `netbox` | NetBox web UI + API | 8000 |
| `netbox-postgres` | PostgreSQL 16 database | - |
| `netbox-redis` | Redis cache + task queue | - |

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

### Starting the Stack

```bash
# From the repo root — starts NetBox and seeds data
make lab-up

# Or manually
docker compose -f shared/docker/docker-compose.yml up -d
uv run python shared/scripts/seed_netbox.py
```

## Containerlab Topology

The `topology.clab.yml` file defines three Arista cEOS switches in a triangle
topology for the Final Boss project.

```
        switch-01
       /         \
      /           \
 switch-02 ----- switch-03
```

### Requirements

- Linux environment (Containerlab does not run natively on macOS)
- Docker
- Containerlab installed (`sudo` access required)
- Arista cEOS ARM64 image (free registration at arista.com)

> **macOS users:** Containerlab must run inside a Linux VM or devcontainer.
> See [docs/containerlab-macos.md](../docs/containerlab-macos.md) for setup
> instructions. Milestones 1-3 do **not** require Containerlab.

### Deploying

```bash
# Linux
make clab-up

# Or directly
sudo containerlab deploy -t shared/docker/topology.clab.yml --reconfigure
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

### Containerlab not found / not supported on macOS

Containerlab requires Linux. On macOS, it must run inside a Linux VM or
devcontainer. See [docs/containerlab-macos.md](../docs/containerlab-macos.md)
for detailed setup instructions.

### Containerlab requires sudo password (Linux)

Containerlab needs root privileges to create network namespaces. Either:

1. Run with sudo: `sudo make clab-up`
2. Configure passwordless sudo for containerlab commands
