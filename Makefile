.PHONY: help lab-up lab-down lab-status lab-destroy seed-netbox \
       clab-up clab-down clab-status test lint clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------
UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)

# Containerlab requires Linux.  On macOS it must run inside a VM.
# See: docs/containerlab-macos.md
ifeq ($(UNAME_S),Darwin)
  CLAB_CMD = @echo ""; \
    echo "=========================================================="; \
    echo "  Containerlab is not supported natively on macOS."; \
    echo "  See docs/containerlab-macos.md for setup instructions."; \
    echo "=========================================================="; \
    echo ""
else
  CLAB_CMD = sudo containerlab
endif

# ---------------------------------------------------------------------------
# Lab lifecycle
# ---------------------------------------------------------------------------

lab-up: ## Start NetBox stack and seed data
	docker compose -f shared/docker/docker-compose.yml up -d
	@echo "Waiting for NetBox to be healthy..."
	@until curl -sf http://localhost:8000/api/ > /dev/null 2>&1; do sleep 3; done
	@echo "NetBox is up. Seeding data..."
	$(MAKE) seed-netbox
	@echo ""
	@echo "============================================================"
	@echo "  NetBox is ready at http://localhost:8000  (admin / admin)"
	@echo "============================================================"
	@echo ""
	@echo "To deploy Containerlab switches, run:  make clab-up"
	@echo "(see docs/containerlab-macos.md if you are on macOS)"

lab-down: ## Stop NetBox (preserves data)
	docker compose -f shared/docker/docker-compose.yml stop

lab-destroy: ## Tear down NetBox (destroys all data)
	docker compose -f shared/docker/docker-compose.yml down -v

lab-status: ## Check the status of all lab components
	@echo "=== Docker Containers ==="
	@docker compose -f shared/docker/docker-compose.yml ps
	@echo ""
	@echo "=== Containerlab Nodes ==="
ifeq ($(UNAME_S),Darwin)
	@echo "(Containerlab does not run natively on macOS — see docs/containerlab-macos.md)"
else
	@sudo containerlab inspect -t shared/docker/topology.clab.yml 2>/dev/null || echo "No topology deployed"
endif

# ---------------------------------------------------------------------------
# Containerlab (Linux only — see docs/containerlab-macos.md for macOS)
# ---------------------------------------------------------------------------

clab-up: ## Deploy Containerlab topology (Linux only)
ifeq ($(UNAME_S),Darwin)
	$(CLAB_CMD)
else
	sudo containerlab deploy -t shared/docker/topology.clab.yml --reconfigure
	@echo ""
	@echo "Containerlab topology is ready."
endif

clab-down: ## Destroy Containerlab topology (Linux only)
ifeq ($(UNAME_S),Darwin)
	$(CLAB_CMD)
else
	sudo containerlab destroy -t shared/docker/topology.clab.yml || true
endif

clab-status: ## Inspect Containerlab nodes (Linux only)
ifeq ($(UNAME_S),Darwin)
	$(CLAB_CMD)
else
	sudo containerlab inspect -t shared/docker/topology.clab.yml
endif

# ---------------------------------------------------------------------------
# Data seeding
# ---------------------------------------------------------------------------

seed-netbox: ## Seed NetBox with course lab data
	uv run python shared/scripts/seed_netbox.py

# ---------------------------------------------------------------------------
# Final Boss project
# ---------------------------------------------------------------------------

boss-server: ## Run the Final Boss MCP server (dev mode)
	cd final-boss && uv run python -m reclaim_agent.server

boss-test: ## Run Final Boss test suite
	cd final-boss && uv run pytest tests/ -v

boss-streamlit: ## Launch the Streamlit AI interface
	cd final-boss && uv run streamlit run src/reclaim_agent/ui.py

# ---------------------------------------------------------------------------
# Quality
# ---------------------------------------------------------------------------

lint: ## Lint all Python files
	uv run ruff check .

test: ## Run all tests
	uv run pytest -v

clean: ## Remove caches and temp files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
