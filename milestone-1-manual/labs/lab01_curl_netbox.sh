#!/usr/bin/env bash
# =============================================================================
# Lab 01: CURL + NetBox
# =============================================================================
#
# In this lab you will use CURL to interact with the NetBox REST API.
# Work through each exercise by filling in the CURL commands where indicated.
#
# Prerequisites:
#   - NetBox running at http://localhost:8000
#   - NETBOX_TOKEN environment variable set:
#       export NETBOX_TOKEN="your-api-token-here"
#   - jq installed (for pretty-printing JSON)
#
# Run this script:
#   chmod +x lab01_curl_netbox.sh
#   ./lab01_curl_netbox.sh
#
# =============================================================================

set -euo pipefail

BASE_URL="http://localhost:8000"

# Verify token is set
if [[ -z "${NETBOX_TOKEN:-}" ]]; then
  echo "ERROR: Set NETBOX_TOKEN environment variable first."
  echo "  export NETBOX_TOKEN='your-token-here'"
  exit 1
fi

echo "=== Lab 01: CURL + NetBox ==="
echo "Using NetBox at: ${BASE_URL}"
echo ""

# -----------------------------------------------------------------------------
# Exercise 1: GET all sites
# -----------------------------------------------------------------------------
# Fetch the list of sites from NetBox and pretty-print the JSON response.
#
# Endpoint: GET /api/dcim/sites/
# Required headers:
#   Authorization: Token $NETBOX_TOKEN
#   Accept: application/json
#
# TODO: Replace the line below with your CURL command
# Hint: curl -s -H "Authorization: ..." -H "Accept: ..." "${BASE_URL}/api/dcim/sites/" | jq .
# -----------------------------------------------------------------------------
echo "--- Exercise 1: GET all sites ---"
echo "TODO: Add your curl command here"
echo ""

# -----------------------------------------------------------------------------
# Exercise 2: GET all devices
# -----------------------------------------------------------------------------
# Fetch the list of devices from NetBox. Print just the device names using jq.
#
# Endpoint: GET /api/dcim/devices/
# jq filter to extract names: .results[].name
#
# TODO: Replace the line below with your CURL command piped to jq
# -----------------------------------------------------------------------------
echo "--- Exercise 2: GET all devices (names only) ---"
echo "TODO: Add your curl command here"
echo ""

# -----------------------------------------------------------------------------
# Exercise 3: GET all IP addresses
# -----------------------------------------------------------------------------
# Fetch all IP addresses and print each address with its status.
#
# Endpoint: GET /api/ipam/ip-addresses/
# jq filter: .results[] | {address, status: .status.value}
#
# TODO: Replace the line below with your CURL command piped to jq
# -----------------------------------------------------------------------------
echo "--- Exercise 3: GET all IP addresses ---"
echo "TODO: Add your curl command here"
echo ""

# -----------------------------------------------------------------------------
# Exercise 4: GET a single device by ID
# -----------------------------------------------------------------------------
# Fetch the device with ID 1 and print its name and device type.
#
# Endpoint: GET /api/dcim/devices/1/
# jq filter: {name, device_type: .device_type.display}
#
# TODO: Replace the line below with your CURL command piped to jq
# -----------------------------------------------------------------------------
echo "--- Exercise 4: GET device ID 1 ---"
echo "TODO: Add your curl command here"
echo ""

# -----------------------------------------------------------------------------
# Exercise 5: GET devices filtered by site
# -----------------------------------------------------------------------------
# Fetch devices that belong to a specific site using a query parameter.
#
# Endpoint: GET /api/dcim/devices/?site=<site-slug>
# Use whatever site slug exists in your NetBox instance.
#
# TODO: Replace the line below with your CURL command
# Hint: add ?site=your-site-slug to the URL
# -----------------------------------------------------------------------------
echo "--- Exercise 5: GET devices filtered by site ---"
echo "TODO: Add your curl command here"
echo ""

# -----------------------------------------------------------------------------
# Exercise 6: POST a new device
# -----------------------------------------------------------------------------
# Create a new device in NetBox.
#
# Endpoint: POST /api/dcim/devices/
# Required headers:
#   Authorization: Token $NETBOX_TOKEN
#   Content-Type: application/json
#   Accept: application/json
#
# Required JSON body fields:
#   name        - string, e.g. "lab-switch-01"
#   role        - integer ID (GET /api/dcim/device-roles/ to find one)
#   device_type - integer ID (GET /api/dcim/device-types/ to find one)
#   site        - integer ID (GET /api/dcim/sites/ to find one)
#   status      - string: "active", "planned", "staged", etc.
#
# TODO: Replace the line below with your CURL POST command
# Hint: curl -s -X POST -H "..." -H "..." -H "..." -d '{ ... }' "${BASE_URL}/api/dcim/devices/" | jq .
# -----------------------------------------------------------------------------
echo "--- Exercise 6: POST a new device ---"
echo "TODO: Add your curl command here"
echo ""

# -----------------------------------------------------------------------------
# Exercise 7: PATCH the device you just created
# -----------------------------------------------------------------------------
# Update the device you created in Exercise 6. Change its status to "planned".
#
# Endpoint: PATCH /api/dcim/devices/<ID>/
# JSON body: {"status": "planned"}
#
# TODO: Replace the line below with your CURL PATCH command
# Note: Replace <ID> with the actual device ID from Exercise 6
# -----------------------------------------------------------------------------
echo "--- Exercise 7: PATCH a device ---"
echo "TODO: Add your curl command here"
echo ""

# -----------------------------------------------------------------------------
# Exercise 8: DELETE the device you created
# -----------------------------------------------------------------------------
# Delete the device from Exercise 6.
#
# Endpoint: DELETE /api/dcim/devices/<ID>/
# Expected response: 204 No Content (empty body)
#
# TODO: Replace the line below with your CURL DELETE command
# Hint: use -w "\nHTTP Status: %{http_code}\n" to see the status code
# -----------------------------------------------------------------------------
echo "--- Exercise 8: DELETE a device ---"
echo "TODO: Add your curl command here"
echo ""

echo "=== Lab 01 Complete ==="
