"""
Reclaim Agent - AI-Powered IP Reclamation MCP Server
=====================================================

This MCP (Model Context Protocol) server provides an AI agent with tools to:
  1. Query NetBox (Source of Truth) for allocated IP addresses
  2. SSH into network devices to pull live ARP and interface data
  3. Cross-reference allocations against live network state
  4. Identify stale/unused IP addresses
  5. Generate reclamation reports
  6. Execute reclamation with human-in-the-loop approval

Students: Your job is to implement the tool stubs in server.py and the
helper modules in the tools/ directory. The skeleton is fully wired up —
you just need to fill in the logic.
"""

__version__ = "0.1.0"
