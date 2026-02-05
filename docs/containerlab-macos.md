# Running Containerlab on macOS (Apple Silicon)

Containerlab requires Linux to create network namespaces and manage container
networking. It **does not run natively on macOS**. This guide covers the
recommended approaches for Apple Silicon Macs (M1/M2/M3/M4).

> **Reference:** [containerlab.dev/macos](https://containerlab.dev/macos/)

---

## Option A: OrbStack VM (Recommended)

OrbStack is a lightweight Docker and Linux VM manager for macOS. It is free
for personal use and provides excellent performance on Apple Silicon.

### 1. Install OrbStack

```bash
brew install orbstack
```

Or download from [orbstack.dev](https://orbstack.dev).

### 2. Create a Linux VM

```bash
orb create ubuntu containerlab-vm
```

### 3. Enter the VM

```bash
orb shell containerlab-vm
```

### 4. Install Containerlab inside the VM

```bash
bash -c "$(curl -sL https://get.containerlab.dev)"
```

### 5. Import your cEOS image

From your macOS terminal, copy the cEOS image into the VM:

```bash
# On macOS — import the cEOS tar into Docker inside the VM
docker --context orbstack import cEOS64-lab-4.32.0F.tar ceos:latest
```

Or from inside the VM:

```bash
docker import cEOS64-lab-4.32.0F.tar ceos:latest
```

### 6. Deploy the lab topology

From inside the VM, navigate to the shared topology file and deploy:

```bash
# Clone or mount your repo inside the VM
cd /path/to/network-automation
sudo containerlab deploy -t shared/docker/topology.clab.yml --reconfigure
```

### 7. Access the switches

The switches will be accessible from inside the VM. To reach them from
macOS, note the VM's IP address:

```bash
orb list   # shows the VM IP
```

Then SSH from macOS:

```bash
ssh admin@<vm-ip> -p <mapped-port>
```

---

## Option B: VS Code Devcontainer

This approach runs Containerlab inside a Docker container using VS Code's
Remote Containers extension. It is the most portable option.

### 1. Create the devcontainer config

Create `.devcontainer/devcontainer.json` in the repo root:

```json
{
  "name": "Network Automation Lab",
  "image": "ghcr.io/srl-labs/containerlab/devcontainer-dind-slim:0.60.0",
  "features": {
    "ghcr.io/devcontainers/features/python:1": {
      "version": "3.12"
    }
  },
  "postCreateCommand": "pip install uv && uv sync --all-extras",
  "forwardPorts": [8000, 11434],
  "remoteUser": "root"
}
```

### 2. Open in VS Code

1. Install the **Dev Containers** extension in VS Code
2. Open the repo folder
3. Press `Cmd+Shift+P` → "Dev Containers: Reopen in Container"
4. Wait for the container to build

### 3. Deploy from inside the container

```bash
sudo clab deploy -t shared/docker/topology.clab.yml --reconfigure
```

---

## Option C: Docker Desktop + Colima

If you already use Docker Desktop or Colima, you can run Containerlab
inside a privileged container:

```bash
docker run --rm -it --privileged \
  --network host \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):/lab \
  -w /lab \
  ghcr.io/srl-labs/containerlab bash

# Inside the container:
containerlab deploy -t shared/docker/topology.clab.yml --reconfigure
```

---

## Arista cEOS on Apple Silicon

Arista provides **ARM64 (aarch64) cEOS images** starting from version 4.32.0F.
Make sure you download the ARM64 variant for Apple Silicon.

### Getting the cEOS image

1. Register for a free account at [arista.com](https://www.arista.com/en/login)
2. Navigate to **Software Downloads → cEOS-lab**
3. Download the **aarch64** variant (e.g., `cEOS64-lab-4.32.0F.tar.xz`)
4. Import into Docker:

```bash
docker import cEOS64-lab-4.32.0F.tar ceos:latest
```

### Verify the architecture

```bash
docker image inspect ceos:latest -f '{{.Architecture}}'
# Expected: arm64
```

> **Important:** If you see `amd64`, you have the wrong image. It will either
> fail to start or run extremely slowly under emulation.

---

## Network Connectivity

When Containerlab runs inside a VM, the switches are not directly accessible
from macOS on `172.20.20.x`. You have several options:

1. **Port forwarding** — Forward SSH ports from the VM to macOS
2. **VM IP routing** — Use the VM's IP address to reach the management network
3. **Run everything in the VM** — Run NetBox, seed scripts, and MCP server
   all inside the VM

For this course, the simplest approach is to **run the seed script and MCP
server from macOS** (they talk to NetBox on localhost:8000) and only use the
VM for the Containerlab switches.

---

## Milestones 1-3 (No Containerlab Needed)

Containerlab is only required for the **Final Boss** project. Milestones 1
through 3 use only NetBox, which runs perfectly on macOS via Docker:

```bash
# Start NetBox (works on macOS natively)
make lab-up

# This gives you everything needed for Milestones 1-3
```

You can complete the majority of the course without Containerlab.

---

## Troubleshooting

### "containerlab: command not found"

Containerlab is not installed on macOS. Follow one of the options above to
run it inside a Linux VM or container.

### cEOS container exits immediately

Check the architecture of your image:

```bash
docker image inspect ceos:latest -f '{{.Architecture}}'
```

If it shows `amd64`, download the ARM64 image from Arista.

### Cannot reach switches from macOS

The switches run inside a VM. See the "Network Connectivity" section above
for options to bridge the gap.

### "Error: cannot create network namespace"

This error confirms you are trying to run Containerlab on macOS directly.
It must run inside a Linux environment (VM or container).
