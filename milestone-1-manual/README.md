# Milestone 1: The "Manual" Era

Learn REST API fundamentals by talking to NetBox with CURL and Python requests.
By the end of this milestone you will be able to read API documentation, make
authenticated requests, and perform CRUD operations against a real network
source of truth.

## Prerequisites

- Lab environment running (`make lab-up` from the repo root)
- Python 3.11+ with dependencies installed (`uv sync --all-extras`)
- `curl` installed

## Environment Setup

The lab automatically provisions NetBox v3.7 with a pre-configured API token.
No manual token creation required.

```bash
# Start the lab (NetBox + seed data)
make lab-up

# The .env.example at the repo root has the default token.
# Copy it if you haven't already:
cp .env.example .env

# For the Python labs, you can also set environment variables directly:
export NETBOX_URL="http://localhost:8000"
export NETBOX_TOKEN="0123456789abcdef0123456789abcdef01234567"
```

| Service | URL | Credentials |
|---------|-----|-------------|
| NetBox UI | http://localhost:8000 | `admin` / `admin` |
| API Token | (pre-configured) | `0123456789abcdef0123456789abcdef01234567` |

## Lessons

| # | Lesson | Description |
|---|--------|-------------|
| 1 | [What Is an API?](lessons/01-what-is-an-api.md) | REST, HTTP verbs, JSON, and networking analogies |
| 2 | [CURL Basics](lessons/02-curl-basics.md) | Making API calls from the terminal with CURL |
| 3 | [Python Requests](lessons/03-python-requests.md) | Translating CURL into Python with the `requests` library |

## Labs

| # | Lab | Description |
|---|-----|-------------|
| 1 | [CURL + NetBox](labs/lab01_curl_netbox.sh) | Bash script exercises: GET, POST against NetBox |
| 2 | [Python + NetBox](labs/lab02_python_requests.py) | Python script exercises: full CRUD against NetBox |

Solutions are in the [solutions/](solutions/) directory. Try the labs yourself
before looking.

## Key Concepts

- **REST API**: A standard way for programs to talk to each other over HTTP
- **CRUD**: Create (POST), Read (GET), Update (PUT/PATCH), Delete (DELETE)
- **Authentication**: NetBox uses token-based auth via the `Authorization` header
- **JSON**: The data format used by virtually all modern APIs
- **NetBox**: An open-source network source of truth (DCIM + IPAM)
