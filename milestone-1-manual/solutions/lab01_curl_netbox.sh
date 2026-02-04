#!/usr/bin/env bash
# =============================================================================
# Lab 01: CURL + NetBox -- SOLUTION
# =============================================================================

set -euo pipefail

BASE_URL="http://localhost:8000"

if [[ -z "${NETBOX_TOKEN:-}" ]]; then
  echo "ERROR: Set NETBOX_TOKEN environment variable first."
  echo "  export NETBOX_TOKEN='your-token-here'"
  exit 1
fi

# Convenience variables
AUTH="Authorization: Token ${NETBOX_TOKEN}"
CT="Content-Type: application/json"
ACCEPT="Accept: application/json"

echo "=== Lab 01: CURL + NetBox (Solution) ==="
echo "Using NetBox at: ${BASE_URL}"
echo ""

# -----------------------------------------------------------------------------
# Exercise 1: GET all sites
# -----------------------------------------------------------------------------
echo "--- Exercise 1: GET all sites ---"
curl -s -H "$AUTH" -H "$ACCEPT" \
  "${BASE_URL}/api/dcim/sites/" | jq .
echo ""

# -----------------------------------------------------------------------------
# Exercise 2: GET all devices (names only)
# -----------------------------------------------------------------------------
echo "--- Exercise 2: GET all devices (names only) ---"
curl -s -H "$AUTH" -H "$ACCEPT" \
  "${BASE_URL}/api/dcim/devices/" | jq '.results[].name'
echo ""

# -----------------------------------------------------------------------------
# Exercise 3: GET all IP addresses
# -----------------------------------------------------------------------------
echo "--- Exercise 3: GET all IP addresses ---"
curl -s -H "$AUTH" -H "$ACCEPT" \
  "${BASE_URL}/api/ipam/ip-addresses/" | jq '.results[] | {address, status: .status.value}'
echo ""

# -----------------------------------------------------------------------------
# Exercise 4: GET a single device by ID
# -----------------------------------------------------------------------------
echo "--- Exercise 4: GET device ID 1 ---"
curl -s -H "$AUTH" -H "$ACCEPT" \
  "${BASE_URL}/api/dcim/devices/1/" | jq '{name, device_type: .device_type.display}'
echo ""

# -----------------------------------------------------------------------------
# Exercise 5: GET devices filtered by site
# -----------------------------------------------------------------------------
echo "--- Exercise 5: GET devices filtered by site ---"
# Get the first site slug dynamically, then filter devices by it
SITE_SLUG=$(curl -s -H "$AUTH" -H "$ACCEPT" \
  "${BASE_URL}/api/dcim/sites/" | jq -r '.results[0].slug // empty')

if [[ -n "${SITE_SLUG}" ]]; then
  echo "Filtering by site: ${SITE_SLUG}"
  curl -s -H "$AUTH" -H "$ACCEPT" \
    "${BASE_URL}/api/dcim/devices/?site=${SITE_SLUG}" | jq '.results[] | {name, site: .site.name}'
else
  echo "No sites found. Create a site first."
fi
echo ""

# -----------------------------------------------------------------------------
# Exercise 6: POST a new device
# -----------------------------------------------------------------------------
echo "--- Exercise 6: POST a new device ---"

# Look up the first available role, device type, and site
ROLE_ID=$(curl -s -H "$AUTH" -H "$ACCEPT" \
  "${BASE_URL}/api/dcim/device-roles/" | jq '.results[0].id')
DTYPE_ID=$(curl -s -H "$AUTH" -H "$ACCEPT" \
  "${BASE_URL}/api/dcim/device-types/" | jq '.results[0].id')
SITE_ID=$(curl -s -H "$AUTH" -H "$ACCEPT" \
  "${BASE_URL}/api/dcim/sites/" | jq '.results[0].id')

echo "Using role=$ROLE_ID, device_type=$DTYPE_ID, site=$SITE_ID"

RESPONSE=$(curl -s -X POST \
  -H "$AUTH" -H "$CT" -H "$ACCEPT" \
  -d "{
    \"name\": \"lab-switch-01\",
    \"role\": ${ROLE_ID},
    \"device_type\": ${DTYPE_ID},
    \"site\": ${SITE_ID},
    \"status\": \"active\"
  }" \
  "${BASE_URL}/api/dcim/devices/")

echo "$RESPONSE" | jq .

# Extract the created device ID for later exercises
DEVICE_ID=$(echo "$RESPONSE" | jq '.id')
echo "Created device ID: ${DEVICE_ID}"
echo ""

# -----------------------------------------------------------------------------
# Exercise 7: PATCH the device
# -----------------------------------------------------------------------------
echo "--- Exercise 7: PATCH a device ---"
if [[ "${DEVICE_ID}" != "null" && -n "${DEVICE_ID}" ]]; then
  curl -s -X PATCH \
    -H "$AUTH" -H "$CT" -H "$ACCEPT" \
    -d '{"status": "planned"}' \
    "${BASE_URL}/api/dcim/devices/${DEVICE_ID}/" | jq '{name, status: .status.value}'
else
  echo "SKIP: No device was created in Exercise 6."
fi
echo ""

# -----------------------------------------------------------------------------
# Exercise 8: DELETE the device
# -----------------------------------------------------------------------------
echo "--- Exercise 8: DELETE a device ---"
if [[ "${DEVICE_ID}" != "null" && -n "${DEVICE_ID}" ]]; then
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE \
    -H "$AUTH" \
    "${BASE_URL}/api/dcim/devices/${DEVICE_ID}/")
  echo "DELETE /api/dcim/devices/${DEVICE_ID}/ -> HTTP ${HTTP_CODE}"
  if [[ "${HTTP_CODE}" == "204" ]]; then
    echo "Device deleted successfully."
  else
    echo "Unexpected status code."
  fi
else
  echo "SKIP: No device to delete."
fi
echo ""

echo "=== Lab 01 Complete ==="
