# Milestone 1: The "Manual" Era

Learn REST API fundamentals by talking to NetBox with CURL and Python requests.
By the end of this milestone you will be able to read API documentation, make
authenticated requests, and perform CRUD operations against a real network
source of truth.

## Prerequisites

- Docker and Docker Compose (to run NetBox locally)
- Python 3.10+
- `curl` installed
- A running NetBox instance at `http://localhost:8000`
- A NetBox API token (Settings > API Tokens in the NetBox UI)

## Environment Setup

```bash
# Export your NetBox token so the labs can use it
export NETBOX_TOKEN="your-api-token-here"

# For the Python labs, create a .env file in the labs/ directory
echo "NETBOX_URL=http://localhost:8000" > labs/.env
echo "NETBOX_TOKEN=your-api-token-here" >> labs/.env

# Install Python dependencies
pip install requests python-dotenv
```

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
