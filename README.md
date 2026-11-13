# ⚡ FastAPI Engineering Suite: From In-Memory CRUD to Cloud-Deployed Auth

A comprehensive, production-grade asynchronous RESTful API engineered with **FastAPI**, managed with Astral's **uv**, and developed across four progressive architectural milestones (Tasks 1–4).

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![uv](https://img.shields.io/badge/uv-Astral%20Tooling-DE5FE9?style=for-the-badge&logo=astral&logoColor=white)](https://docs.astral.sh/uv/)
[![Supabase](https://img.shields.io/badge/Supabase-Auth%20%26%20JWT-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
[![Docker](https://img.shields.io/badge/Docker-PostgreSQL%20Stack-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![SQLite](https://img.shields.io/badge/SQLite-ACID%20Persistence-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![FastAPI Cloud](https://img.shields.io/badge/FastAPI%20Cloud-Live%20Production-059669?style=for-the-badge&logo=fastapi&logoColor=white)](https://crud-api-2b23f883.fastapicloud.dev/docs)

---

## 🌐 Live Production Deployment

The latest milestone (**Task 4: Authentication & Protected Routes**) is live and accessible globally on **FastAPI Cloud**:

- **Production Base URL:** [`https://crud-api-2b23f883.fastapicloud.dev`](https://crud-api-2b23f883.fastapicloud.dev)
- **Interactive Swagger UI (with Bearer Padlock):** [`https://crud-api-2b23f883.fastapicloud.dev/docs`](https://crud-api-2b23f883.fastapicloud.dev/docs)
- **Cloud Health Probe:** [`https://crud-api-2b23f883.fastapicloud.dev/health`](https://crud-api-2b23f883.fastapicloud.dev/health)

```bash
# Instant verification of the live cloud deployment:
curl -i https://crud-api-2b23f883.fastapicloud.dev/public/info
# Returns: {"message":"Welcome stranger! This info is public."}
```

---

## 📑 Table of Contents

- [Executive Summary & Core Milestones](#executive-summary--core-milestones)
- [Key Engineering Feats](#key-engineering-feats)
- [Architecture & Evolutionary Progression](#architecture--evolutionary-progression)
- [Repository Structure & Organization](#repository-structure--organization)
- [Quickstart & Installation](#quickstart--installation)
- [Running Any Milestone (Tasks 1–4)](#running-any-milestone-tasks-14)
- [API Specification & Complete Endpoint Reference](#api-specification--complete-endpoint-reference)
  - [Task 4: Authentication & Access Control](#task-4-authentication--access-control)
  - [Tasks 1–3: Tasks Management CRUD](#tasks-13-tasks-management-crud)
  - [Terminal Verification Workflows via cURL](#terminal-verification-workflows-via-curl)
- [Interactive API Documentation (Swagger & ReDoc)](#interactive-api-documentation-swagger--redoc)
- [Architectural Deep Dives](#architectural-deep-dives)
  - [Task 1: In-Memory Storage & Zero-Trust Validation](#task-1-in-memory-storage--zero-trust-validation)
  - [Task 2: Embedded SQLite Persistence & Schema Evolution](#task-2-embedded-sqlite-persistence--schema-evolution)
  - [Task 3: Containerized PostgreSQL & Docker Compose](#task-3-containerized-postgresql--docker-compose)
  - [Task 4: Supabase Auth, JWT Verification & HTTPBearer Security](#task-4-supabase-auth-jwt-verification--httpbearer-security)
- [Direct Database Exploration (SQL Workflows)](#direct-database-exploration-sql-workflows)
- [AI vs Me: Benchmark & Architectural Audit (Tasks 1–3)](#ai-vs-me-benchmark--architectural-audit-tasks-13)
- [Contract Proof: "Storage is an Implementation Detail"](#contract-proof-storage-is-an-implementation-detail)
- [Production Deployment Architectures](#production-deployment-architectures)
- [Versioning, Tags & Release History](#versioning-tags--release-history)
- [Proprietary License & Ownership](#proprietary-license--ownership)

---

## Executive Summary & Core Milestones

This repository traces the evolution of a backend service through four distinct architectural paradigms, preserving each milestone cleanly while advancing to cloud-ready microservices:

| Milestone | Architecture | Storage Layer | Primary Entrypoint | Release Tag | Status |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Task 1** | Ephemeral In-Memory REST API | In-process Python dictionaries | `backend/task1_main.py` | `v1.0.0` | ✅ Complete |
| **Task 2** | Embedded ACID SQL Persistence | In-process SQLite (`database/tasks.db`) | `backend/task2_main.py` | `v1.1.0` | ✅ Complete |
| **Task 3** | Containerized Multi-Tier Stack | Dockerized PostgreSQL 16 + Compose | `backend/task3_main.py` | `v1.3.0` | ✅ Complete |
| **Task 4** | Cloud Auth, JWT & Protected Routes | Supabase Auth + FastAPI Cloud | `backend/main.py` | `v1.4.0` | ✅ Complete |

---

## Key Engineering Feats

- **Stateless JWT Security & Authorization**: Implemented standard RFC 7519 Bearer token verification via Supabase Auth, extracting cryptographically validated user metadata and strictly isolating public vs. protected resources.
- **Interactive Swagger UI Security Schemes**: Configured OpenAPI `HTTPBearer(auto_error=False)` allowing direct in-browser authentication and token-gated endpoint execution via Swagger's green **Authorize 🔓** padlock.
- **Zero-Downtime Cloud Deployment**: Deployed natively to **FastAPI Cloud** with cloud environment variable injection (`SUPABASE_URL`, `SUPABASE_KEY`) and automated readiness health checking (`GET /health`).
- **Zero-Trust Input Validation**: Rigidly parses incoming JSON bodies via Pydantic; empty or whitespace-only strings are rejected with clean `400 Bad Request` responses before touching downstream logic.
- **Multiple Storage Backends with Unbroken Contracts**: Transformed storage from in-memory lists to SQLite and then PostgreSQL without modifying external HTTP response contracts, verified by shared regression suites.
- **ACID Transaction Guarantees & Self-Healing Schemas**: All database interactions execute inside atomic transaction contexts (`with conn:`). Startups automatically initialize schemas and idempotent seeds without race conditions.
- **Ultra-Fast Developer Velocity with Astral uv**: Sub-second dependency resolution, deterministic locking via `uv.lock`, and zero-configuration execution via `uv run`.

---

## Architecture & Evolutionary Progression

The system evolved from a standalone single-file service into a distributed, authenticated cloud architecture:

```text
               ┌────────────────────────────────────────────────────────┐
               │                CLIENT REQUEST / BROWSER                │
               └───────────────────────────┬────────────────────────────┘
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
        [PUBLIC ENDPOINTS]                              [PROTECTED ENDPOINTS]
    GET /health, GET /public/info                 GET /protected/profile, /dashboard
    POST /auth/signup, /auth/login                        POST /auth/logout
                    │                                             │
                    │                                             ▼
                    │                               ┌───────────────────────────┐
                    │                               │ HTTPBearer Security Gate  │
                    │                               │ (FastAPI Dependency Auth) │
                    │                               └─────────────┬─────────────┘
                    │                                             │
                    │                                             ▼
                    │                               ┌───────────────────────────┐
                    │                               │   Supabase Token Guard    │
                    │                               │   supabase.auth.get_user  │
                    │                               └─────────────┬─────────────┘
                    │                                             │
                    │               ┌─────────────────────────────┘
                    ▼               ▼
        ┌────────────────────────────────────────────────────────────────────────┐
        │                       FASTAPI REQUEST DISPATCHER                       │
        │                                                                        │
        │  Task 4: Auth Handlers ──► Supabase Cloud API                          │
        │  Task 3: Tasks CRUD    ──► Containerized PostgreSQL (psycopg 3 / %s)   │
        │  Task 2: Tasks CRUD    ──► Embedded SQLite (database/tasks.db / ?)     │
        │  Task 1: Tasks CRUD    ──► In-Memory Dictionary Store                  │
        └────────────────────────────────────────────────────────────────────────┘
```

---

## Repository Structure & Organization

```text
CRUD_API/
├── backend/
│   ├── main.py          # Task 4: Supabase Auth & JWT API (Current default entrypoint)
│   ├── task3_main.py    # Task 3: Containerized PostgreSQL CRUD API
│   ├── task2_main.py    # Task 2: Embedded SQLite CRUD API with auto-lifespan
│   └── task1_main.py    # Task 1: In-memory CRUD API baseline
├── ai-version/
│   ├── main.py          # Task 3: Quarantined AI Postgres implementation (rematch)
│   ├── task2_main.py    # Task 2: Quarantined AI SQLite implementation (rematch)
│   ├── task1_main.py    # Task 1: Quarantined AI in-memory implementation
│   ├── Dockerfile       # Task 3: AI multi-stage container image
│   └── compose.yaml     # Task 3: AI isolated Compose stack (port 8001)
├── database/
│   └── tasks.db         # SQLite database file, auto-generated on boot (git-ignored)
├── tests/
│   └── test_api.py      # Shared contract test suite running across storage backends
├── Docs/
│   ├── Task 1 API - Project Brief.pdf
│   ├── Task 2 API Database - Project Brief.pdf
│   ├── Task 3 Containerize Stack - Project Brief.pdf
│   ├── Task 4 Auth - Project Brief.pdf
│   └── *.png            # Verification screenshots & Swagger UI captures
├── compose.yaml         # Task 3: Hand-built API + PostgreSQL container stack
├── dockerfile           # Task 3: Hand-built FastAPI container image
├── pyproject.toml       # Project metadata, CLI entrypoint & dependencies
├── requirements.txt     # Pinned Python package requirements
├── uv.lock              # Cryptographically locked Astral uv dependency tree
├── .env.example         # Template environment variables (PostgreSQL & Supabase)
├── .gitignore           # Excludes .env, *.db, __pycache__, and temporary caches
├── LICENSE              # Proprietary ownership and licensing agreement
├── tests.md             # Comprehensive test execution manual (Tasks 1–4)
└── README.md            # Master architectural documentation
```

### Entrypoint Configuration
Configured in `pyproject.toml` so `uv run fastapi dev` automatically boots the current Task 4 Auth API from repository root:

```toml
[tool.fastapi]
entrypoint = "backend.main:app"
```

---

## Quickstart & Installation

### Prerequisites
- **Python 3.10+**
- **Astral uv** (Recommended modern toolchain):
  ```bash
  # macOS / Linux:
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Windows PowerShell:
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **Docker & Docker Compose** (Required only for Task 3 container stack).

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/TridentifyIshaan/CRUD_API.git
cd CRUD_API

# Create and activate virtual environment with uv:
uv venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# Install all project dependencies deterministically:
uv sync
```

### 2. Configure Environment Variables
Copy the template and supply your credentials:
```bash
cp .env.example .env
```
Ensure your `.env` contains:
```ini
# Supabase Authentication (Required for Task 4):
SUPABASE_URL=https://<your-project-id>.supabase.co
SUPABASE_KEY=<your-anon-public-key>

# PostgreSQL Configuration (Required for Task 3):
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=taskdb
DATABASE_URL=postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}
```

---

## Running Any Milestone (Tasks 1–4)

Each task is fully runnable independently:

| Milestone / Target | Execution Command | Listening Port | Storage Backend |
| :--- | :--- | :---: | :--- |
| **Task 4 (Auth API - Current)** | `uv run fastapi dev backend/main.py` | `8000` | Supabase Cloud Auth |
| **Task 3 (Postgres + Docker)** | `docker compose up --build` | `8000` | Containerized PostgreSQL |
| **Task 3 (Postgres - Local app)** | `uv run fastapi dev backend/task3_main.py` | `8000` | Local PostgreSQL instance |
| **Task 2 (SQLite Database)** | `uv run fastapi dev backend/task2_main.py` | `8000` | Embedded `database/tasks.db` |
| **Task 1 (In-Memory)** | `uv run fastapi dev backend/task1_main.py` | `8000` | In-memory Python list |
| **AI Task 3 Rematch Stack** | `docker compose -f ai-version/compose.yaml up --build`| `8001` | Isolated Postgres (`ai_taskdata`) |
| **AI Task 2 Rematch (SQLite)** | `uv run fastapi dev ai-version/task2_main.py --port 8001`| `8001` | `ai-version/tasks.db` |
| **AI Task 1 Rematch (Memory)** | `uv run fastapi dev ai-version/task1_main.py --port 8001`| `8001` | In-memory store |

---

## API Specification & Complete Endpoint Reference

### Task 4: Authentication & Access Control

| Method | Endpoint | HTTP Status | Description | Security Header | Request Payload |
| :---: | :--- | :---: | :--- | :---: | :---: |
| `GET` | `/` | `200 OK` | Service metadata & Supabase connection confirmation | None | None |
| `GET` | `/health` | `200 OK` | Health probe for monitoring & cloud readiness | None | None |
| `POST` | `/auth/signup` | `201` / `400` | Register a new user with Supabase Auth | None | `{"email": "str", "password": "str"}` |
| `POST` | `/auth/login` | `200` / `400` / `401` | Authenticate user & receive access + refresh JWTs | None | `{"email": "str", "password": "str"}` |
| `POST` | `/auth/logout` | `204` / `401` | Invalidate user session | `Bearer <token>` | None |
| `GET` | `/public/info` | `200 OK` | Public unauthenticated route | None | None |
| `GET` | `/protected/profile`| `200` / `401` | Retrieve authenticated user ID, email, and metadata | `Bearer <token>` | None |
| `GET` | `/protected/dashboard`| `200` / `401` | Access dashboard protected via reusable dependency | `Bearer <token>` | None |

### Tasks 1–3: Tasks Management CRUD

*Preserved in `backend/task1_main.py`, `backend/task2_main.py`, and `backend/task3_main.py`.*

| Method | Endpoint | HTTP Status | Description | Query Parameters | Request Payload |
| :---: | :--- | :---: | :--- | :---: | :---: |
| `GET` | `/tasks` | `200 OK` / `400` | List all tasks | `?done=`, `?search=`, `?sort=` | None |
| `GET` | `/tasks/{id}` | `200` / `404` | Fetch task by integer ID | None | None |
| `POST` | `/tasks` | `201` / `400` | Create task with non-empty title | None | `{"title": "string"}` |
| `PUT` | `/tasks/{id}` | `200` / `400` / `404` | Update title, done status, or both | None | `{"title"?: "str", "done"?: bool}` |
| `DELETE` | `/tasks/{id}` | `204` / `404` | Delete task by ID (empty response body) | None | None |
| `GET` | `/stats` | `200 OK` | Summary metrics: `{"total", "done", "pending"}` | None | None |

---

### Terminal Verification Workflows via cURL

#### 1. Complete Task 4 Authentication Workflow
```bash
# A. Register a new user
curl -i -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "developer@example.com", "password": "secure_password_123"}'
# HTTP/1.1 201 Created -> {"message": "User created successfully"}

# B. Log in to acquire JWT access token
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "developer@example.com", "password": "secure_password_123"}')
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# C. Access public route (No token required)
curl -i http://localhost:8000/public/info
# HTTP/1.1 200 OK -> {"message": "Welcome stranger! This info is public."}

# D. Attempt protected profile access WITHOUT token (Rejection)
curl -i http://localhost:8000/protected/profile
# HTTP/1.1 401 Unauthorized -> {"error": "Access token required"}

# E. Access protected profile WITH Bearer token (Success)
curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer $TOKEN"
# HTTP/1.1 200 OK -> {"id": "...", "email": "developer@example.com", "created_at": "..."}

# F. Access protected dashboard via reusable middleware dependency
curl -i http://localhost:8000/protected/dashboard \
  -H "Authorization: Bearer $TOKEN"
# HTTP/1.1 200 OK -> {"message": "Welcome to your protected dashboard!", "user_id": "..."}

# G. Log out / Terminate session
curl -i -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer $TOKEN"
# HTTP/1.1 204 No Content (empty body)
```

#### 2. Tasks Management CRUD Workflow (Tasks 1–3)
```bash
# List tasks
curl -i http://localhost:8000/tasks

# Create a task (201 Created)
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Deploy staging build"}'

# Input validation rejection on empty payload (400 Bad Request)
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{}'
# HTTP/1.1 400 Bad Request -> {"error": "Title is required and cannot be empty"}

# Update task status (200 OK)
curl -i -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'

# Delete task (204 No Content with empty body)
curl -i -X DELETE http://localhost:8000/tasks/1
```

---

## Interactive API Documentation (Swagger & ReDoc)

FastAPI automatically dynamically models route decorators, Pydantic schemas, and security dependencies into interactive documentation interfaces:

| Interface | Local Development URL | Production Cloud URL | Purpose |
| :--- | :--- | :--- | :--- |
| **Swagger UI** | [http://localhost:8000/docs](http://localhost:8000/docs) | [https://crud-api-2b23f883.fastapicloud.dev/docs](https://crud-api-2b23f883.fastapicloud.dev/docs) | Interactive testing playground with direct execution & Authorize padlock |
| **ReDoc** | [http://localhost:8000/redoc](http://localhost:8000/redoc) | [https://crud-api-2b23f883.fastapicloud.dev/redoc](https://crud-api-2b23f883.fastapicloud.dev/redoc) | Structured, responsive human-readable API reference |
| **OpenAPI Schema** | [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json) | [https://crud-api-2b23f883.fastapicloud.dev/openapi.json](https://crud-api-2b23f883.fastapicloud.dev/openapi.json) | Machine-readable OpenAPI 3.1 specification contract |

### Interactive Bearer Token Padlock in Swagger
Stage 5 integrated `HTTPBearer(auto_error=False)` into the security scheme:
1. Open `/docs` in your browser.
2. Click the green **Authorize 🔓** button at the top right.
3. Paste an `access_token` obtained from `POST /auth/login`.
4. Click **Authorize** → The padlock locks 🔒, and all subsequent requests sent via Swagger UI include the `Authorization: Bearer <token>` header automatically!

---

## Architectural Deep Dives

### Task 1: In-Memory Storage & Zero-Trust Validation
- **Architecture**: Ephemeral in-process list of Python dictionaries (`tasks = [...]`).
- **Validation**: Enforced zero-trust validation on inputs. Missing titles, empty strings, and whitespace-only payloads (`"   "`) are rejected immediately with `400 Bad Request`.
- **Status Codes**: Strict compliance with standard REST codes (`200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `404 Not Found`).

### Task 2: Embedded SQLite Persistence & Schema Evolution
- **Architecture**: In-process ACID-compliant SQLite database resolved at `database/tasks.db`.
- **Automatic Lifecycle & Self-Healing**: Managed via FastAPI `@asynccontextmanager lifespan`. If the file or directory is missing, it automatically creates the directory, initializes tables, and seeds starter records idempotently (verifying `COUNT(*) == 0`).
- **Schema Migration on Boot**: Older databases lacking timestamp columns are dynamically updated via `ALTER TABLE tasks ADD COLUMN created_at TEXT` during server boot.
- **SQL Injection Prevention**: All queries use parameterized SQL (`?` placeholders).

### Task 3: Containerized PostgreSQL & Docker Compose
- **Architecture**: Multi-tier architecture orchestrating an unprivileged FastAPI application container and a dedicated **PostgreSQL 16** container over an isolated internal Docker bridge network (`tasknet`).
- **Connection Management**: High-performance PostgreSQL driver (`psycopg` v3) utilizing binary protocol bindings and dictionary row factories (`dict_row`).
- **Named Volume Persistence**: Persistent volume (`taskdata`) ensures database records survive complete container teardowns (`docker compose down`).
- **Fail-Fast Configuration**: Requires `.env` configuration; missing credentials raise immediate exceptions preventing unauthenticated boots.

### Task 4: Supabase Auth, JWT Verification & HTTPBearer Security
- **Architecture**: Stateless authentication powered by Supabase GoTrue Auth and RFC 7519 JSON Web Tokens (ES256 signatures).
- **Cryptographic Gate**: The server does not store session tables; it verifies token integrity and validity using `supabase.auth.get_user(token)`. Tampered signatures or expired tokens return `401 Unauthorized`.
- **Reusable Dependency Guard**: Reusable FastAPI dependency `get_current_user` injects authenticated user state into route handlers (`Depends(get_current_user)`).

---

## Direct Database Exploration (SQL Workflows)

Direct SQL inspection performed during Stage 4 against `database/tasks.db` using `sqlite3` CLI in table mode (`.mode table`):

### 1. Retrieve All Tasks
```sql
SELECT * FROM tasks;
```
![SELECT All Tasks](Docs/sql_select_all.png)

### 2. Filter Completed Tasks
```sql
SELECT * FROM tasks WHERE done = 1;
```
![SELECT Completed Tasks](Docs/sql_select_completed.png)

### 3. Aggregate Task Count
```sql
SELECT COUNT(*) FROM tasks;
```
![SELECT COUNT](Docs/sql_select_count.png)

### 4. Direct SQL Mutation by Hand
```sql
UPDATE tasks SET done = 1 WHERE id = 2;
```
![UPDATE Task](Docs/sql_update.png)

### 5. Direct Deletion by Hand
```sql
DELETE FROM tasks WHERE id = 3;
```
![DELETE Task](Docs/sql_delete.png)

---

## AI vs Me: Benchmark & Architectural Audit (Tasks 1–3)

Across Tasks 1, 2, and 3, an AI assistant was challenged to implement the same project specifications in quarantine (`ai-version/`) and benchmarked against the hand-crafted codebase:

| Metric / Dimension | Hand-Crafted Engineering | Quarantined AI Generation (Round 1) | AI Rematch (Prompt Refined) |
| :--- | :--- | :--- | :--- |
| **Concurrency Model** | Native `async def` on main event loop | Synchronous `def` offloaded to threadpool | Converted to native `async def` |
| **Error Contract** | Consistent `{"error": "<msg>"}` & `400` | Default FastAPI `{"detail": ...}` & `422` | Strict `400` and `{"error": ...}` enforced |
| **Image Size (Docker)**| 495 MB (`COPY . .`) | 310 MB (Multi-stage non-root build) | Maintained lightweight multi-stage image |
| **Database Port Safety**| Postgres private to Docker network | Exposed `5433:5432` to host machine | Closed host port, private network only |
| **Partial Updates** | Two queries (SELECT then UPDATE) | Single atomic query (`COALESCE` + `RETURNING`)| Single atomic query (`COALESCE` + `RETURNING`)|
| **Seed Concurrency** | Count check on startup | Missing table lock (potential race)| Added `LOCK TABLE` concurrency guard |

### Key Engineering Takeaway
AI implementations often produce elegant low-level optimizations (e.g., multi-stage container builds, SQL `COALESCE` updates) but frequently experience **silent specification drift** (e.g., reverting async routes, altering status code conventions, exposing internal ports) unless the prompt acts as an exhaustive architectural contract.

---

## Contract Proof: "Storage is an Implementation Detail"

A fundamental design goal was ensuring that swapping storage backends (Python list → SQLite → PostgreSQL) never altered the HTTP contract.

[`tests/test_api.py`](tests/test_api.py) runs identical regression tests against both the In-Memory API (`backend/task1_main.py`) and SQLite API (`backend/task2_main.py`):

```bash
uv run pytest -v
```

Passing the exact same test suite confirms that to external clients, storage is purely an internal implementation detail.

---

## Production Deployment Architectures

### 1. Cloud-Native Deployment (FastAPI Cloud)
Task 4 is packaged and hosted on FastAPI Cloud with automatic SSL and zero-downtime rolling updates:
- **Build Strategy**: Native Astral uv container assembly.
- **Environment Management**: Secrets injected via `fastapi env set SUPABASE_URL` and `SUPABASE_KEY`.
- **Health Verification**: Cloud probes monitor `GET /health` before routing traffic.

### 2. Containerized Deployment (Docker Compose)
Task 3 provides production container orchestration:
```bash
docker compose up -d --build
```
- **Service Isolation**: PostgreSQL is unreachable from the outside host, communicating solely across the private Docker network `tasknet`.
- **Data Durability**: Backed by a named Docker volume (`taskdata`).

---

## Versioning, Tags & Release History

This project strictly adheres to [Semantic Versioning 2.0.0](https://semver.org/). Every milestone is permanently recorded with an annotated git tag:

| Tag | Phase | Milestone Summary |
| :--- | :---: | :--- |
| `v1.0.0` | **Task 1** | Final release: In-memory CRUD API with zero-trust validation & test suite |
| `v1.1.0-alpha.1`..`6` | **Task 2** | Pre-releases: SQLite integration, lifespan auto-seeding, and SQL CLI exploration |
| `v1.1.0` | **Task 2** | Final release: SQLite persistent database API & AI benchmark audit |
| `v1.2.0` | **Task 2** | Extras release: SQL filtering, search, sorting, stats, and unified error formats |
| `v1.3.0-alpha.1`..`6` | **Task 3** | Pre-releases: Docker PostgreSQL integration, `psycopg` 3, and Compose stack |
| `v1.3.0` | **Task 3** | Final release: Containerized PostgreSQL stack with Docker Compose |
| `v1.3.1` | **Task 3** | AI rematch release: Refined AI stack restoring `/health` contract & network isolation |
| `v1.4.0a1` | **Task 4** | Stage 0: Supabase SDK initialization, client lifecycle & `.env` configuration |
| `v1.4.0a2` | **Task 4** | Stage 1: User registration (`POST /auth/signup`) & login (`POST /auth/login`) with JWT |
| `v1.4.0a3` | **Task 4** | Stage 2: Public route (`GET /public/info`) & unverified protected gate (`GET /protected/profile`)|
| `v1.4.0a4` | **Task 4** | Stage 3: Cryptographic JWT verification via Supabase `get_user` guard |
| `v1.4.0a5` | **Task 4** | Stage 4: Reusable FastAPI auth dependency, protected dashboard & `POST /auth/logout` |
| `v1.4.0a6` | **Task 4** | Stage 5: Swagger UI documentation with interactive `HTTPBearer` Authorize padlock |
| `v1.4.0` | **Task 4** | **Final Release: Live FastAPI Cloud production deployment & master documentation** |

```bash
# View all tagged milestones:
git tag -l

# Checkout any historical milestone:
git checkout v1.0.0
```

---

## Proprietary License & Ownership

**Copyright © 2026 Ishaan Rastogi. All Rights Reserved.**

This repository, its architectural designs, source code, and schemas are confidential and proprietary work. See [LICENSE](LICENSE) for full legal terms. No reproduction, modification, or distribution is permitted without prior written consent.
