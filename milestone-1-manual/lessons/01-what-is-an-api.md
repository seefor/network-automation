# Lesson 1: What Is an API?

## The Networking Analogy

You already understand APIs. Think about how a router handles a packet:

1. A packet arrives with a **destination** (URL)
2. It uses a **protocol** (HTTP, like TCP/UDP)
3. It carries a **payload** (JSON data, like the packet body)
4. The router sends back a **response** (status code + data)

A REST API works the same way. Instead of forwarding packets between networks,
you are sending structured requests to a server and getting structured responses
back.

## REST in 60 Seconds

REST (Representational State Transfer) is a set of conventions for building APIs
over HTTP. The key ideas:

- **Resources** have URLs. A device in NetBox lives at `/api/dcim/devices/1/`.
- **HTTP verbs** define the action (GET, POST, PUT, PATCH, DELETE).
- **Representations** are JSON objects that describe the resource.
- **Stateless**: every request carries all the information the server needs.
  There is no "session" the way there is with an SSH CLI.

Think of it like SNMP, but human-readable. Instead of OIDs, you have URLs.
Instead of ASN.1 encoding, you have JSON.

## HTTP Verbs (The CRUD Map)

| Verb   | Action | SNMP Equivalent | Example                          |
|--------|--------|-----------------|----------------------------------|
| GET    | Read   | GET             | List all devices                 |
| POST   | Create | SET (new row)   | Add a new device                 |
| PUT    | Replace| SET (full)      | Replace all fields on a device   |
| PATCH  | Update | SET (partial)   | Change just the device name      |
| DELETE | Delete | -               | Remove a device                  |

**PUT vs PATCH**: PUT replaces the entire resource (you must send every field).
PATCH updates only the fields you include. In practice, PATCH is what you will
use 90% of the time.

## Anatomy of an HTTP Request

```
POST /api/dcim/devices/ HTTP/1.1     <-- verb + path
Host: localhost:8000                  <-- target server
Authorization: Token abc123def456    <-- authentication
Content-Type: application/json       <-- "I'm sending JSON"
Accept: application/json             <-- "Send me JSON back"

{                                    <-- request body (JSON payload)
  "name": "spine-01",
  "role": 1,
  "device_type": 1,
  "site": 1
}
```

The server responds:

```
HTTP/1.1 201 Created                 <-- status code
Content-Type: application/json

{                                    <-- response body
  "id": 42,
  "name": "spine-01",
  "role": { "id": 1, "name": "Spine" },
  ...
}
```

## HTTP Status Codes

You will see these constantly. Memorize the categories:

| Range | Meaning       | Common Codes                              |
|-------|---------------|-------------------------------------------|
| 2xx   | Success       | 200 OK, 201 Created, 204 No Content       |
| 3xx   | Redirect      | 301 Moved, 304 Not Modified               |
| 4xx   | Client Error  | 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 405 Method Not Allowed |
| 5xx   | Server Error  | 500 Internal Server Error, 502 Bad Gateway |

**Networking parallel**: Status codes are like ICMP messages. A 404 is
"Destination Unreachable". A 401 is "Administratively Prohibited". A 500 is
"the remote router crashed".

## JSON

JSON (JavaScript Object Notation) is the data format you will work with.
If you have ever looked at structured data in YAML (like an Ansible vars file),
JSON is similar but with different syntax.

### Data types

```json
{
  "hostname": "leaf-01",          // string
  "port_count": 48,               // number (integer)
  "is_active": true,              // boolean
  "uplinks": ["Eth1/49", "Eth1/50"],  // array (list)
  "location": {                   // object (nested dict)
    "site": "dc-east",
    "rack": "R01"
  },
  "decommission_date": null       // null (no value)
}
```

### Navigating nested JSON

NetBox API responses are nested. When you GET a device, the `site` field is
not just an ID -- it is an object:

```json
{
  "id": 1,
  "name": "spine-01",
  "site": {
    "id": 1,
    "url": "http://localhost:8000/api/dcim/sites/1/",
    "name": "DC-East"
  }
}
```

To get the site name in Python: `device["site"]["name"]`
To get it with `jq`: `.site.name`

## Authentication

NetBox uses token-based authentication. Every request must include:

```
Authorization: Token <your-token>
```

This is like an SNMP community string, but sent as an HTTP header instead of
embedded in the protocol. Tokens can be scoped to read-only or read-write and
can be revoked without changing passwords.

**Never hardcode tokens in scripts.** Use environment variables or `.env` files.

## The NetBox API

NetBox organizes its API by app:

| App    | Prefix           | Resources                        |
|--------|------------------|----------------------------------|
| DCIM   | `/api/dcim/`     | sites, devices, interfaces, cables |
| IPAM   | `/api/ipam/`     | ip-addresses, prefixes, vlans    |
| Circuits | `/api/circuits/` | circuits, providers             |
| Tenancy | `/api/tenancy/`  | tenants, tenant-groups          |

Every resource supports the standard CRUD operations via HTTP verbs.

### List vs Detail endpoints

- **List**: `GET /api/dcim/devices/` -- returns a paginated list
- **Detail**: `GET /api/dcim/devices/1/` -- returns a single device (by ID)

List responses are wrapped in a pagination envelope:

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/dcim/devices/?limit=50&offset=50",
  "previous": null,
  "results": [ ... ]
}
```

The actual objects are inside `results`. Always access `.results` when working
with list endpoints.

### Filtering

Add query parameters to filter list results:

```
GET /api/dcim/devices/?site=dc-east&role=leaf
GET /api/ipam/ip-addresses/?parent=10.0.0.0/24
```

### The browsable API

Open `http://localhost:8000/api/` in your browser. NetBox gives you a
clickable, self-documenting API explorer. Use it constantly.

## Summary

| Concept         | Networking Analogy                    |
|-----------------|---------------------------------------|
| URL / endpoint  | Destination IP + port                 |
| HTTP verb       | The operation (like SNMP GET vs SET)  |
| JSON body       | Packet payload                        |
| Status code     | ICMP response                         |
| Auth token      | SNMP community string                 |
| REST API        | SNMP/NETCONF but human-readable       |

Next: [Lesson 2 - CURL Basics](02-curl-basics.md)
