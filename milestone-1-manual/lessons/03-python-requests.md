# Lesson 3: Python Requests

The `requests` library is CURL for Python. Everything you did in Lesson 2
translates directly.

## Installation

```bash
pip install requests python-dotenv
```

## CURL to Python: Side by Side

### CURL

```bash
curl -s \
  -H "Authorization: Token $NETBOX_TOKEN" \
  -H "Accept: application/json" \
  "http://localhost:8000/api/dcim/devices/"
```

### Python

```python
import requests

url = "http://localhost:8000/api/dcim/devices/"
headers = {
    "Authorization": f"Token {NETBOX_TOKEN}",
    "Accept": "application/json",
}

response = requests.get(url, headers=headers)
data = response.json()
print(data)
```

The mapping is direct:

| CURL                     | Python requests                        |
|--------------------------|----------------------------------------|
| `-X GET`                 | `requests.get()`                       |
| `-X POST`               | `requests.post()`                      |
| `-X PATCH`              | `requests.patch()`                     |
| `-X PUT`                | `requests.put()`                       |
| `-X DELETE`             | `requests.delete()`                    |
| `-H "Header: value"`    | `headers={"Header": "value"}`          |
| `-d '{"key":"val"}'`    | `json={"key": "val"}`                  |
| `\| jq .`               | `response.json()`                      |
| URL query params         | `params={"site": "dc-east"}`           |

## Loading Configuration from .env

Never hardcode tokens. Use `python-dotenv`:

```python
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env file in current directory

NETBOX_URL: str = os.getenv("NETBOX_URL", "http://localhost:8000")
NETBOX_TOKEN: str = os.getenv("NETBOX_TOKEN", "")
```

Your `.env` file:

```
NETBOX_URL=http://localhost:8000
NETBOX_TOKEN=your-api-token-here
```

Add `.env` to `.gitignore`. Never commit tokens.

## Building a Reusable Session

`requests.Session()` lets you set headers once and reuse them:

```python
import requests

session = requests.Session()
session.headers.update({
    "Authorization": f"Token {NETBOX_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json",
})

# Now every request through this session includes those headers
response = session.get(f"{NETBOX_URL}/api/dcim/devices/")
```

This is the equivalent of the reusable bash functions from Lesson 2.

## The Response Object

```python
response = session.get(f"{NETBOX_URL}/api/dcim/devices/")

response.status_code   # 200
response.ok            # True (status < 400)
response.json()        # parsed JSON as a Python dict
response.text          # raw response body as string
response.headers       # response headers dict
response.url           # the final URL (after redirects)
```

## GET: Reading Data

### List all devices

```python
response = session.get(f"{NETBOX_URL}/api/dcim/devices/")
response.raise_for_status()  # raises exception if 4xx/5xx
data: dict = response.json()

for device in data["results"]:
    print(f"{device['name']} - {device['site']['name']}")
```

### Get a single device

```python
device_id: int = 1
response = session.get(f"{NETBOX_URL}/api/dcim/devices/{device_id}/")
response.raise_for_status()
device: dict = response.json()
print(device["name"])
```

### Filter with query parameters

```python
# These are equivalent:
response = session.get(f"{NETBOX_URL}/api/dcim/devices/?site=dc-east")
response = session.get(f"{NETBOX_URL}/api/dcim/devices/", params={"site": "dc-east"})
```

Use `params=` -- it handles URL encoding for you.

### Paginating through all results

```python
def get_all(session: requests.Session, url: str) -> list[dict]:
    """Fetch all pages from a paginated NetBox endpoint."""
    results: list[dict] = []
    while url:
        response = session.get(url)
        response.raise_for_status()
        data: dict = response.json()
        results.extend(data["results"])
        url = data.get("next")  # None when no more pages
    return results

all_devices: list[dict] = get_all(session, f"{NETBOX_URL}/api/dcim/devices/")
```

## POST: Creating Data

```python
new_device: dict = {
    "name": "leaf-03",
    "role": 1,
    "device_type": 1,
    "site": 1,
    "status": "active",
}

response = session.post(f"{NETBOX_URL}/api/dcim/devices/", json=new_device)
response.raise_for_status()
created: dict = response.json()
print(f"Created device ID: {created['id']}")
```

Use `json=` (not `data=`). The `json=` parameter automatically:
- Serializes the dict to a JSON string
- Sets `Content-Type: application/json`

## PATCH: Updating Data

```python
device_id: int = created["id"]
updates: dict = {"status": "planned"}

response = session.patch(
    f"{NETBOX_URL}/api/dcim/devices/{device_id}/",
    json=updates,
)
response.raise_for_status()
updated: dict = response.json()
print(f"Status is now: {updated['status']['value']}")
```

## DELETE: Removing Data

```python
device_id: int = created["id"]
response = session.delete(f"{NETBOX_URL}/api/dcim/devices/{device_id}/")
response.raise_for_status()
# 204 No Content -- empty body
print(f"Deleted device {device_id}")
```

## Error Handling

### Basic: raise_for_status

```python
response = session.get(f"{NETBOX_URL}/api/dcim/devices/9999/")
response.raise_for_status()  # raises requests.exceptions.HTTPError for 404
```

### Better: check and handle

```python
response = session.post(f"{NETBOX_URL}/api/dcim/devices/", json=payload)

if response.ok:
    print(f"Created: {response.json()['name']}")
else:
    print(f"Error {response.status_code}: {response.json()}")
```

NetBox returns detailed error messages in the response body:

```json
{
  "name": ["A device with this name already exists."],
  "device_type": ["This field is required."]
}
```

### Production: structured error handling

```python
try:
    response = session.post(f"{NETBOX_URL}/api/dcim/devices/", json=payload)
    response.raise_for_status()
except requests.exceptions.ConnectionError:
    print("Cannot reach NetBox. Is it running?")
except requests.exceptions.HTTPError as exc:
    print(f"HTTP {exc.response.status_code}: {exc.response.json()}")
```

## Full Working Example

```python
#!/usr/bin/env python3
"""List all devices and their primary IPs from NetBox."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

NETBOX_URL: str = os.getenv("NETBOX_URL", "http://localhost:8000")
NETBOX_TOKEN: str = os.getenv("NETBOX_TOKEN", "")


def main() -> None:
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Token {NETBOX_TOKEN}",
        "Accept": "application/json",
    })

    response = session.get(f"{NETBOX_URL}/api/dcim/devices/")
    response.raise_for_status()

    for device in response.json()["results"]:
        primary_ip: str = "N/A"
        if device.get("primary_ip"):
            primary_ip = device["primary_ip"]["address"]
        print(f"{device['name']:20s} {primary_ip}")


if __name__ == "__main__":
    main()
```

## Quick Reference

```python
# Setup
session = requests.Session()
session.headers.update({"Authorization": f"Token {TOKEN}"})

# CRUD
session.get(url)                         # Read
session.get(url, params={"key": "val"})  # Read with filters
session.post(url, json=payload)          # Create
session.patch(url, json=updates)         # Partial update
session.put(url, json=full_object)       # Full replace
session.delete(url)                      # Delete

# Response
response.status_code  # int
response.ok           # bool
response.json()       # dict
response.raise_for_status()  # raise on error
```

Next: [Lab 1 - CURL + NetBox](../labs/lab01_curl_netbox.sh)
