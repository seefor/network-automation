# Lesson 2: CURL Basics

CURL is the network engineer's packet generator for HTTP. Before writing Python
scripts, you should be able to poke any API directly from your terminal.

## Why CURL First?

- Zero dependencies (already on your machine)
- You see the raw HTTP request and response
- Easy to copy/paste from API docs
- Great for debugging ("does the API work, or is my code broken?")

## CURL Anatomy

```bash
curl -s -X GET \
  -H "Authorization: Token $NETBOX_TOKEN" \
  -H "Accept: application/json" \
  "http://localhost:8000/api/dcim/devices/"
```

Breaking it down:

| Flag | Meaning |
|------|---------|
| `-s` | Silent mode (hide progress bar) |
| `-X GET` | HTTP verb (GET is default, so optional here) |
| `-H "..."` | Add an HTTP header |
| `"http://..."` | The URL (always quote it) |

Other flags you will use:

| Flag | Meaning |
|------|---------|
| `-d '{"key":"val"}'` | Send a JSON request body |
| `-X POST` | Use POST verb |
| `-X PATCH` | Use PATCH verb |
| `-X DELETE` | Use DELETE verb |
| `-v` | Verbose: show full request and response headers |
| `-o file.json` | Write output to a file |
| `-w "\n"` | Append a newline after output |

## GET: Read Data

### List all devices

```bash
curl -s \
  -H "Authorization: Token $NETBOX_TOKEN" \
  -H "Accept: application/json" \
  "http://localhost:8000/api/dcim/devices/" | jq .
```

The `| jq .` at the end pretty-prints the JSON. Install `jq` if you do not
have it (`brew install jq` / `apt install jq`).

The response is paginated:

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    { "id": 1, "name": "spine-01", ... },
    { "id": 2, "name": "leaf-01", ... }
  ]
}
```

### Get a single device

```bash
curl -s \
  -H "Authorization: Token $NETBOX_TOKEN" \
  -H "Accept: application/json" \
  "http://localhost:8000/api/dcim/devices/1/" | jq .
```

### Filter devices by site

```bash
curl -s \
  -H "Authorization: Token $NETBOX_TOKEN" \
  -H "Accept: application/json" \
  "http://localhost:8000/api/dcim/devices/?site=dc-east" | jq .
```

### List IP addresses

```bash
curl -s \
  -H "Authorization: Token $NETBOX_TOKEN" \
  -H "Accept: application/json" \
  "http://localhost:8000/api/ipam/ip-addresses/" | jq .
```

### Extract specific fields with jq

```bash
# Just the device names
curl -s \
  -H "Authorization: Token $NETBOX_TOKEN" \
  -H "Accept: application/json" \
  "http://localhost:8000/api/dcim/devices/" | jq '.results[].name'

# Device name and site name
curl -s \
  -H "Authorization: Token $NETBOX_TOKEN" \
  -H "Accept: application/json" \
  "http://localhost:8000/api/dcim/devices/" | jq '.results[] | {name, site: .site.name}'
```

## POST: Create Data

To create a resource, send a POST with a JSON body.

### Create a device

```bash
curl -s -X POST \
  -H "Authorization: Token $NETBOX_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "name": "leaf-03",
    "role": 1,
    "device_type": 1,
    "site": 1,
    "status": "active"
  }' \
  "http://localhost:8000/api/dcim/devices/" | jq .
```

Key points:
- `-X POST` sets the verb
- `-H "Content-Type: application/json"` tells the server "my body is JSON"
- `-d '{...}'` is the request body
- NetBox returns the created object with a `201 Created` status

**What IDs do I use?** You need the numeric IDs for related objects (role,
device_type, site). GET those list endpoints first to find the IDs, or use
NetBox slugs where the API supports them.

### Create an IP address

```bash
curl -s -X POST \
  -H "Authorization: Token $NETBOX_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "address": "10.0.1.1/24",
    "status": "active",
    "description": "Loopback for leaf-03"
  }' \
  "http://localhost:8000/api/ipam/ip-addresses/" | jq .
```

## PATCH: Update Data

PATCH sends only the fields you want to change.

```bash
curl -s -X PATCH \
  -H "Authorization: Token $NETBOX_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "status": "planned"
  }' \
  "http://localhost:8000/api/dcim/devices/1/" | jq .
```

This changes only the `status` field on device 1. Everything else stays the
same.

## DELETE: Remove Data

```bash
curl -s -X DELETE \
  -H "Authorization: Token $NETBOX_TOKEN" \
  "http://localhost:8000/api/dcim/devices/99/"
```

A successful delete returns `204 No Content` with an empty body.

## Debugging with -v

When something goes wrong, add `-v` to see the full conversation:

```bash
curl -v -X GET \
  -H "Authorization: Token $NETBOX_TOKEN" \
  -H "Accept: application/json" \
  "http://localhost:8000/api/dcim/devices/"
```

This shows:
- `>` lines: what you sent
- `<` lines: what the server returned (including status code and headers)

Common errors:

| Status | Likely Cause |
|--------|-------------|
| 401    | Bad or missing token |
| 403    | Token does not have write permission |
| 400    | Malformed JSON or missing required fields |
| 404    | Wrong URL or object does not exist |
| 405    | Wrong HTTP verb for that endpoint |

## Saving CURL as a Reusable Script

Set defaults so you do not repeat yourself:

```bash
#!/usr/bin/env bash
BASE_URL="http://localhost:8000"
AUTH_HEADER="Authorization: Token ${NETBOX_TOKEN}"

# Reusable function
nb_get() {
  curl -s -H "$AUTH_HEADER" -H "Accept: application/json" "${BASE_URL}${1}"
}

nb_post() {
  curl -s -X POST \
    -H "$AUTH_HEADER" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d "$2" \
    "${BASE_URL}${1}"
}

# Usage
nb_get "/api/dcim/devices/" | jq .
nb_post "/api/dcim/devices/" '{"name":"test","role":1,"device_type":1,"site":1}'
```

## Quick Reference

```bash
# GET (list)
curl -s -H "Authorization: Token $T" "http://localhost:8000/api/dcim/devices/" | jq .

# GET (detail)
curl -s -H "Authorization: Token $T" "http://localhost:8000/api/dcim/devices/1/" | jq .

# POST (create)
curl -s -X POST -H "Authorization: Token $T" -H "Content-Type: application/json" \
  -d '{"name":"new-device","role":1,"device_type":1,"site":1}' \
  "http://localhost:8000/api/dcim/devices/" | jq .

# PATCH (update)
curl -s -X PATCH -H "Authorization: Token $T" -H "Content-Type: application/json" \
  -d '{"status":"planned"}' \
  "http://localhost:8000/api/dcim/devices/1/" | jq .

# DELETE
curl -s -X DELETE -H "Authorization: Token $T" "http://localhost:8000/api/dcim/devices/1/"
```

Next: [Lesson 3 - Python Requests](03-python-requests.md)
