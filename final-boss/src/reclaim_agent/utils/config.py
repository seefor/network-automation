"""
Application Configuration
==========================

Uses Pydantic BaseSettings to load and validate configuration from
environment variables and/or a .env file.

SETUP:
  1. Copy .env.example to .env in the project root
  2. Fill in your NetBox URL, API token, and device credentials
  3. The Settings class will auto-load these when the server starts

All fields are validated at startup — if a required field is missing,
you'll get a clear error message telling you what to set.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file.

    Required environment variables:
        NETBOX_URL           - Base URL of your NetBox instance
        NETBOX_TOKEN         - API token for NetBox authentication
        DEVICE_USERNAME      - SSH username for network devices
        DEVICE_PASSWORD      - SSH password for network devices

    Optional environment variables:
        DEVICE_ENABLE_PASSWORD - Enable/privileged mode password (if required)
        MCP_SERVER_HOST        - Host to bind the MCP server to (default: localhost)
        MCP_SERVER_PORT        - Port for the MCP server (default: 8080)
    """

    # -- NetBox connection --
    NETBOX_URL: str = "http://localhost:8000"
    NETBOX_TOKEN: str = "change-me"

    # -- Device SSH credentials --
    DEVICE_USERNAME: str = "admin"
    DEVICE_PASSWORD: str = "admin"
    DEVICE_ENABLE_PASSWORD: str | None = None

    # -- MCP server settings --
    MCP_SERVER_HOST: str = "localhost"
    MCP_SERVER_PORT: int = 8080

    model_config = {
        # Load from .env file in the current working directory
        "env_file": ".env",
        # Don't fail if .env file doesn't exist (fall back to env vars / defaults)
        "env_file_encoding": "utf-8",
        # Allow extra fields in the environment without raising errors
        "extra": "ignore",
    }
