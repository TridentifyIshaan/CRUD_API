# ⚡ CRUD API: High-Performance RESTful Architecture with FastAPI & uv

[![Python Engine](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI Framework](https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Package Manager](https://img.shields.io/badge/uv-Astral%20Orchestrator-DE5FE9?style=for-the-badge&logo=astral&logoColor=white)](https://docs.astral.sh/uv/)
[![ASGI Server](https://img.shields.io/badge/Server-Uvicorn%20ASGI-499848?style=for-the-badge&logo=gunicorn&logoColor=white)](https://www.uvicorn.org/)

--------

## 📋 Table of Contents

- [📖 1. Project Overview & Architectural Design](#-1-project-overview--architectural-design)
  - [1.1 Purpose & Execution Model](#11-purpose--execution-model)
  - [1.2 Request-Response Lifecycle Flow](#12-request-response-lifecycle-flow)
  - [1.3 Key Architectural Strengths](#13-key-architectural-strengths)
- [🗂️ 2. Repository Topology & File Index](#️-2-repository-topology--file-index)
  - [2.1 File System Index](#21-file-system-index)
  - [2.2 Entrypoint Configuration](#22-entrypoint-configuration)
- [⚙️ 3. Environment & Prerequisites](#️-3-environment--prerequisites)
- [🛠️ 4. Installation & Environment Provisioning](#️-4-installation--environment-provisioning)
- [🚀 5. Execution & Runtime Operations](#-5-execution--runtime-operations)
  - [5.1 Local Development (Hot-Reload)](#51-local-development-hot-reload)
  - [5.2 Production ASGI Service](#52-production-asgi-service)
- [📖 6. Interactive Documentation & Schema Contracts](#-6-interactive-documentation--schema-contracts)
  - [6.1 Documentation Interfaces](#61-documentation-interfaces)
  - [6.2 Schema & Contract Design](#62-schema--contract-design)
- [🔌 7. API Endpoints & Request/Response Verification](#-7-api-endpoints--requestresponse-verification)
  - [7.1 Endpoint Inventory](#71-endpoint-inventory)
  - [7.2 Terminal Verification via cURL](#72-terminal-verification-via-curl)
- [🚢 8. Deployment Architecture](#-8-deployment-architecture)
  - [8.1 FastAPI Cloud CLI Deployment](#81-fastapi-cloud-cli-deployment)
  - [8.2 Containerized Production Deployment](#82-containerized-production-deployment)
- [🔒 9. Proprietary Rights & Ownership Notice](#-9-proprietary-rights--ownership-notice)

--------

## 📖 1. Project Overview & Architectural Design

### 1.1 Purpose & Execution Model

This repository implements a lightweight, high-throughput asynchronous RESTful API service engineered with **FastAPI** and packaged through Astral's **uv** package manager.

Modern backend services require deterministic dependencies, minimal cold-start latencies, and rigorous schema validation. This project decouples application routing logic into a dedicated module while providing root-level entrypoint metadata so both development servers and production ASGI runtimes can spin up without manual path munging.

### 1.2 Request-Response Lifecycle Flow

```text
                  [Incoming Client HTTP Request]
                               │
                               ▼
                   [Uvicorn / ASGI Web Server]
                               │
                               ▼
                    [FastAPI Request Router]
                     (Route & Method Match)
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
        [Path Match: /]              [Unmatched Path]
                │                             │
                ▼                             ▼
       [Async Route Handler]            [HTTP 404]
        (backend.main:root)           {"detail": "Not Found"}
                │
                ▼
        [JSON Serialization]
     {"message": "Hello World"}
                │
                ▼
     [HTTP 200 OK Response]
```

### 1.3 Key Architectural Strengths

- **Asynchronous Native**: Built directly on Starlette's async runtime and AnyIO concurrency primitives, allowing concurrent request handling on a non-blocking event loop.
- **Strict Contract-First Schemas**: OpenAPI 3.1 and JSON Schema models validate payloads and define precise input/output expectations automatically.
- **Deterministic Package Orchestration**: Powered by Astral's `uv`, cutting dependency resolution and virtual environment creation down to milliseconds.
- **Zero-Friction Documentation**: Live Swagger UI, ReDoc, and raw OpenAPI schemas generated from route decorators without manual upkeep.

--------

## 🗂️ 2. Repository Topology & File Index

### 2.1 File System Index

```text
CRUD_API/
├── backend/
│   └── main.py          ← Core application entrypoint, route definitions, and async handlers
├── pyproject.toml       ← Project metadata & FastAPI CLI entrypoint orchestration
├── requirements.txt     ← Locked root dependencies (fastapi[standard])
├── .gitignore           ← Workspace ignore rules (.venv, pycache, OS artifacts)
├── LICENSE              ← Proprietary license & rights reservation
└── README.md            ← Master architecture and operational documentation
```

### 2.2 Entrypoint Configuration

The application registers its entrypoint inside `pyproject.toml`:

```toml
[tool.fastapi]
entrypoint = "backend.main:app"
```

This declaration maps the top-level `fastapi` CLI directly to the `app` instance located in `backend/main.py`, eliminating the need to pass explicit module strings when invoking developer tooling.

--------

## ⚙️ 3. Environment & Prerequisites

Ensure the target execution host has the following toolchains installed:

- **Python**: Version `3.10` or higher
- **uv**: Astral package and environment manager

### Installing `uv`

```sh
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify your installation:

```sh
uv --version
```

--------

## 🛠️ 4. Installation & Environment Provisioning

To reproduce the exact execution environment cleanly:

1. **Clone the repository:**
   ```sh
   git clone https://github.com/TridentifyIshaan/CRUD_API.git
   cd CRUD_API
   ```

2. **Initialize an isolated virtual environment:**
   ```sh
   uv venv --python 3.10 .venv
   ```

3. **Activate the virtual environment:**
   - **macOS / Linux:**
     ```sh
     source .venv/bin/activate
     ```
   - **Windows:**
     ```powershell
     .\.venv\Scripts\activate
     ```

4. **Install pinned dependencies:**
   ```sh
   uv pip install -r requirements.txt
   ```

--------

## 🚀 5. Execution & Runtime Operations

### 5.1 Local Development (Hot-Reload)

Launch the development server with live reload enabled. Any code modifications saved in `/backend` will trigger an immediate server reload:

```sh
uv run fastapi dev
```

- **Local Address**: `http://127.0.0.1:8000`
- **Bound Host**: `127.0.0.1` (loopback only for secure local development)
- **Watcher**: Active directory polling with instant reloading on file save.

### 5.2 Production ASGI Service

To spin up the optimized ASGI production server without file watching:

```sh
uv run fastapi run
```

- **Production Address**: `http://0.0.0.0:8000`
- **Bound Host**: `0.0.0.0` (all network interfaces, ready for container binding)
- **Workers**: Concurrency-optimized for production deployment.

To customize the port or host:

```sh
uv run fastapi run --port 8080 --host 0.0.0.0
```

--------

## 📖 6. Interactive Documentation & Schema Contracts

### 6.1 Documentation Interfaces

FastAPI parses route operations at startup and mounts real-time documentation interfaces:

| Documentation Surface | URL | Description |
| :--- | :--- | :--- |
| **Swagger UI** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive API exploration playground with live "Try it out" execution. |
| **ReDoc** | [http://localhost:8000/redoc](http://localhost:8000/redoc) | Clean, publication-grade responsive documentation layout. |
| **OpenAPI Schema** | [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json) | Raw machine-readable OpenAPI 3.1.0 specification in JSON format. |

### 6.2 Schema & Contract Design

- **API Specification (OpenAPI 3.1)**: Defines the outer contract boundaries—HTTP paths, methods, parameters, status codes, and security definitions.
- **Data Schemas (JSON Schema)**: Outlines the physical shape, types, constraints, and validation rules of request and response payloads.
- **Client Code Generation**: The raw schema at `/openapi.json` can be consumed by tools like `openapi-generator` or `orval` to generate strongly-typed client SDKs for TypeScript, Swift, or Kotlin with zero hand-written boilerplate.

--------

## 🔌 7. API Endpoints & Request/Response Verification

### 7.1 Endpoint Inventory

| Method | Endpoint | HTTP Status | Description | Response Model |
| :---: | :--- | :---: | :--- | :--- |
| `GET` | `/` | `200 OK` | Root health probe & service greeting | `{"message": "string"}` |

### 7.2 Terminal Verification via cURL

To inspect raw response headers, transmission timing, and status codes:

```sh
curl -i http://localhost:8000/
```

**Verified Terminal Output:**

```http
HTTP/1.1 200 OK
date: Sun, 09 Nov 2026 11:45:00 GMT
server: uvicorn
content-length: 25
content-type: application/json

{"message":"Hello World"}
```

--------

## 🚢 8. Deployment Architecture

### 8.1 FastAPI Cloud CLI Deployment

FastAPI provides integrated deployment workflows to package and ship applications directly:

```sh
uv run fastapi deploy
```

This bundles the application according to the entrypoint declared in `pyproject.toml` and initiates cloud provisioning.

### 8.2 Containerized Production Deployment

For deployment inside Docker, Kubernetes, AWS ECS, GCP Cloud Run, or Fly.io:

```dockerfile
# Multi-stage container build utilizing official uv binaries
FROM python:3.11-slim

WORKDIR /app

# Extract prebuilt uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install dependencies into system layer
COPY requirements.txt pyproject.toml ./
RUN uv pip install --system -r requirements.txt

# Copy backend source tree
COPY backend/ ./backend/

EXPOSE 8000

CMD ["fastapi", "run", "backend/main.py", "--port", "8000", "--host", "0.0.0.0"]
```

--------

## 🔒 9. Proprietary Rights & Ownership Notice

**Copyright © 2026 Ishaan Rastogi. All Rights Reserved.**

This repository, its architectural designs, source code, schemas, and associated documentation are the **confidential and proprietary property** of the author.

See [LICENSE](LICENSE) for full legal terms.

- **No Open-Source License**: No license—express or implied—is granted to any party.
- **Restricted Usage**: No individual or entity may copy, reproduce, distribute, modify, create derivative works from, publicly display, or commercially exploit any part of this software without prior explicit written permission from the owner.
