.PHONY: help lab-up lab-down lab-status lab-destroy seed-netbox test lint clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Lab lifecycle
# ---------------------------------------------------------------------------

lab-up: ## Start the full lab (NetBox + mock switches + seed data)
	docker compose -f shared/docker/docker-compose.yml up -d
	@echo "Waiting for NetBox to be healthy..."
	@until curl -sf http://localhost:8000/api/ > /dev/null 2>&1; do sleep 3; done
	@echo "NetBox is up. Seeding data..."
	$(MAKE) seed-netbox
	@echo ""
	@echo "============================================================"
	@echo "  Lab is ready!"
	@echo "  NetBox:    http://localhost:8000  (admin / admin)"
	@echo "  switch-01: ssh -p 2201 admin@localhost  (password: admin)"
	@echo "  switch-02: ssh -p 2202 admin@localhost  (password: admin)"
	@echo "  switch-03: ssh -p 2203 admin@localhost  (password: admin)"
	@echo "============================================================"

lab-down: ## Stop the lab (preserves data)
	docker compose -f shared/docker/docker-compose.yml stop

lab-destroy: ## Tear down the lab (destroys all data)
	docker compose -f shared/docker/docker-compose.yml down -v

lab-status: ## Check the status of all lab components
	@echo "=== Lab Containers ==="
	@docker compose -f shared/docker/docker-compose.yml ps

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
