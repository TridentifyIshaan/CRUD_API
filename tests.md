# 🧪 Test Execution Manual (Tasks 1, 2, 3 & 4)

Comprehensive testing guide, assertion checklists, and verification checkpoints for:
- **Task 1**: In-Memory CRUD API (`backend/task1_main.py`)
- **Task 2**: Embedded SQLite Database CRUD API (`backend/task2_main.py`)
- **Task 3**: Containerized PostgreSQL & Docker Compose Stack (`backend/task3_main.py`)
- **Task 4**: Supabase Authentication & Protected Routes (`backend/main.py` & Live Cloud)

---

## 📑 Table of Contents

- [Target Server Launch Matrix](#target-server-launch-matrix)
- [Task 1: In-Memory CRUD API Tests (T1)](#task-1-in-memory-crud-api-tests-t1)
  - [T1 - Stage 0: Base Server Liveness](#t1---stage-0-base-server-liveness)
  - [T1 - Stage 1: Service Discovery & Health Check](#t1---stage-1-service-discovery--health-check)
  - [T1 - Stage 2: Read Operations & 404 Handling](#t1---stage-2-read-operations--404-handling)
  - [T1 - Stage 3: Create with Zero-Trust Validation](#t1---stage-3-create-with-zero-trust-validation)
  - [T1 - Stage 4: Update & Delete Operations](#t1---stage-4-update--delete-operations)
  - [T1 - Stage 5: Swagger UI Audit](#t1---stage-5-swagger-ui-audit)
  - [T1 - Stage 6: Git Delivery Audit](#t1---stage-6-git-delivery-audit)
  - [T1 - Stage 7: AI Rematch Diff](#t1---stage-7-ai-rematch-diff)
- [Task 2: SQLite Database CRUD API Tests (T2)](#task-2-sqlite-database-crud-api-tests-t2)
  - [T2 - Stage 0: Database & Lifecycle Setup](#t2---stage-0-database--lifecycle-setup)
  - [T2 - Stage 1: Read from SQLite](#t2---stage-1-read-from-sqlite)
  - [T2 - Stage 2: Create in SQLite & Restart Persistence](#t2---stage-2-create-in-sqlite--restart-persistence)
  - [T2 - Stage 3: Update & Delete via SQL](#t2---stage-3-update--delete-via-sql)
  - [T2 - Stage 4: Direct SQL Exploration in CLI](#t2---stage-4-direct-sql-exploration-in-cli)
  - [T2 - Stage 5: Clean Clone & Self-Healing Verification](#t2---stage-5-clean-clone--self-healing-verification)
  - [T2 - Stage 6: AI vs Me Migration Diff](#t2---stage-6-ai-vs-me-migration-diff)
  - [T2 - Extras: Filter, Search, Sort & Statistics](#t2---extras-filter-search-sort--statistics)
- [Task 3: Containerized PostgreSQL & Docker Stack (T3)](#task-3-containerized-postgresql--docker-stack-t3)
  - [T3 - Stage 0: Postgres in Docker & Secret Exclusion](#t3---stage-0-postgres-in-docker--secret-exclusion)
  - [T3 - Stage 1: Connect via .env & Table Seeding](#t3---stage-1-connect-via-env--table-seeding)
  - [T3 - Stage 2: Read from Postgres](#t3---stage-2-read-from-postgres)
  - [T3 - Stage 3: Full CRUD Operations in SQL](#t3---stage-3-full-crud-operations-in-sql)
  - [T3 - Stage 4: Docker Compose Full Stack Orchestration](#t3---stage-4-docker-compose-full-stack-orchestration)
  - [T3 - Stage 5: One-Command Boot & Clean Clone Round-Trip](#t3---stage-5-one-command-boot--clean-clone-round-trip)
  - [T3 - Stage 6: AI vs Me Containerized Stack](#t3---stage-6-ai-vs-me-containerized-stack)
- [Task 4: Supabase Authentication & Cloud API Tests (T4)](#task-4-supabase-authentication--cloud-api-tests-t4)
  - [T4 - Stage 0: Setup Supabase SDK & Connection Lifecycle](#t4---stage-0-setup-supabase-sdk--connection-lifecycle)
  - [T4 - Stage 1: User Registration & Token Issuance](#t4---stage-1-user-registration--token-issuance)
  - [T4 - Stage 2: Public vs Protected Gate Extraction](#t4---stage-2-public-vs-protected-gate-extraction)
  - [T4 - Stage 3: Cryptographic Token Verification Guard](#t4---stage-3-cryptographic-token-verification-guard)
  - [T4 - Stage 4: Reusable Dependency & Session Termination](#t4---stage-4-reusable-dependency--session-termination)
  - [T4 - Stage 5: Interactive Swagger UI Bearer Security](#t4---stage-5-interactive-swagger-ui-bearer-security)
  - [T4 - Stage 6: Live Production Cloud Deployment](#t4---stage-6-live-production-cloud-deployment)
- [Automated Regression Suites & Runners](#automated-regression-suites--runners)
  - [1. Shared Contract Test Suite (`pytest`)](#1-shared-contract-test-suite-pytest)
  - [2. One-Click Terminal Verification Script](#2-one-click-terminal-verification-script)

---

## Target Server Launch Matrix

Before executing test cases, ensure the corresponding target server is running from repository root (`CRUD_API`):

| Test Target | Launch Command | Target URL | Documentation |
| :--- | :--- | :--- | :--- |
| **Task 4 (Auth - Current)** | `uv run fastapi dev backend/main.py` | `http://localhost:8000` | `http://localhost:8000/docs` |
| **Task 4 (Live Cloud)** | *(Already running in cloud)* | `https://crud-api-2b23f883.fastapicloud.dev` | `https://crud-api-2b23f883.fastapicloud.dev/docs` |
| **Task 3 (Postgres Stack)** | `docker compose up --build` | `http://localhost:8000` | `http://localhost:8000/docs` |
| **Task 2 (SQLite Database)**| `uv run fastapi dev backend/task2_main.py` | `http://localhost:8000` | `http://localhost:8000/docs` |
| **Task 1 (In-Memory)** | `uv run fastapi dev backend/task1_main.py` | `http://localhost:8000` | `http://localhost:8000/docs` |

---

## Task 1: In-Memory CRUD API Tests (T1)

### T1 - Stage 0: Base Server Liveness
Verify that the ASGI server boots and accepts incoming TCP connections.
```bash
curl -i http://localhost:8000/
```
- **Assertion:** Status code `200 OK`, JSON body contains discovery metadata.

---

### T1 - Stage 1: Service Discovery & Health Check

#### 1. Root Service Discovery (`GET /`)
```bash
curl -s http://localhost:8000/ | jq .
```
- **Assertion:** Returns API name, version, and endpoints list:
```json
{
  "name": "Task API",
  "version": "1.0",
  "endpoints": ["/tasks", "/health"]
}
```

#### 2. Health Probe (`GET /health`)
```bash
curl -i http://localhost:8000/health
```
- **Assertion:**
```http
HTTP/1.1 200 OK
content-type: application/json

{"status":"ok"}
```

---

### T1 - Stage 2: Read Operations & 404 Handling

#### 1. Fetch All Tasks (`GET /tasks`)
```bash
curl -i http://localhost:8000/tasks
```
- **Assertion:** Returns `HTTP 200 OK` with 3 seeded tasks.

#### 2. Lookup Valid Task ID (`GET /tasks/1`)
```bash
curl -i http://localhost:8000/tasks/1
```
- **Assertion:** Returns `HTTP 200 OK` with task record `{"id": 1, ...}`.

#### 3. Lookup Non-Existent Task ID (`GET /tasks/999`)
```bash
curl -i http://localhost:8000/tasks/999
```
- **Assertion:** Returns `HTTP 404 Not Found` with `{"detail": "Task 999 not found"}`.

---

### T1 - Stage 3: Create with Zero-Trust Validation

#### 1. Successful Task Creation (`POST /tasks`)
```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Implement input validation"}'
```
- **Assertion:** Returns `HTTP 201 Created` with newly generated `id`, `title`, and `done: false`.

#### 2. Validation: Empty Payload (`POST /tasks`)
```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{}'
```
- **Assertion:** Returns `HTTP 400 Bad Request` with `{"detail": "Title is required and cannot be empty"}`.

#### 3. Validation: Whitespace Only (`POST /tasks`)
```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "   "}'
```
- **Assertion:** Returns `HTTP 400 Bad Request`.

---

### T1 - Stage 4: Update & Delete Operations

#### 1. Partial Update: Mark Task Done (`PUT /tasks/1`)
```bash
curl -i -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```
- **Assertion:** Returns `HTTP 200 OK` with `"done": true`.

#### 2. Update Validation: Empty Body (`PUT /tasks/1`)
```bash
curl -i -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{}'
```
- **Assertion:** Returns `HTTP 400 Bad Request` with `{"detail": "Must provide title or done to update"}`.

#### 3. Delete Task (`DELETE /tasks/1`)
```bash
curl -i -X DELETE http://localhost:8000/tasks/1
```
- **Assertion:** Returns `HTTP 204 No Content` with an empty response body (`Content-Length: 0`).

#### 4. Delete Verification (`GET /tasks/1`)
```bash
curl -i http://localhost:8000/tasks/1
```
- **Assertion:** Returns `HTTP 404 Not Found`.

---

### T1 - Stage 5: Swagger UI Audit
Verify that OpenAPI interactive documentation renders properly at `http://localhost:8000/docs`.

### T1 - Stage 6: Git Delivery Audit
Verify clean semantic commits for each stage in git log.

### T1 - Stage 7: AI Rematch Diff
Benchmark hand-crafted `backend/task1_main.py` against `ai-version/task1_main.py`.

---

## Task 2: SQLite Database CRUD API Tests (T2)

### T2 - Stage 0: Database & Lifecycle Setup

#### Test 0.1: SQLite File & Table Schema Verification
```bash
sqlite3 database/tasks.db ".schema tasks"
sqlite3 database/tasks.db "SELECT COUNT(*) FROM tasks;"
```
- **Assertion:** Table exists with columns (`id`, `title`, `done`, `created_at`, `updated_at`) and seeded count >= 2.

#### Test 0.2: Idempotent Seeding & Restart Test
Restart the server multiple times:
```bash
# Seed count must remain constant:
sqlite3 database/tasks.db "SELECT COUNT(*) FROM tasks;"
```
- **Assertion:** Row count does not duplicate on server restart.

#### Test 0.3: Clean Clone / Self-Healing Test
```bash
rm database/tasks.db
# Start server briefly to trigger lifespan:
python3 -c "from backend.task2_main import init_db; init_db()"
test -f database/tasks.db && echo "Database self-healed!"
```
- **Assertion:** SQLite file and initial seed tasks recreate automatically.

---

### T2 - Stage 1: Read from SQLite

#### Test 1.1: Fetch All Tasks from SQLite (`GET /tasks`)
```bash
curl -i http://localhost:8000/tasks
```
- **Assertion:** Returns `HTTP 200 OK` reading live records from SQLite.

#### Test 1.2: Fetch Single Task (`GET /tasks/1`)
```bash
curl -i http://localhost:8000/tasks/1
```
- **Assertion:** Returns `HTTP 200 OK` with record 1.

#### Test 1.3: Fetch Non-Existent Task (`GET /tasks/999`)
```bash
curl -i http://localhost:8000/tasks/999
```
- **Assertion:** Returns `HTTP 404 Not Found` with `{"error": "Task not found"}`.

---

### T2 - Stage 2: Create in SQLite & Restart Persistence

#### Test 2.1: Successful Task Creation (`POST /tasks`)
```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Verify SQLite Persistence"}'
```
- **Assertion:** Returns `HTTP 201 Created` with allocated ID.

#### Test 2.2: The Restart Test (Persistence Proof)
1. Stop the server (`Ctrl+C`).
2. Start the server again.
3. Query the newly created task:
```bash
curl -i http://localhost:8000/tasks
```
- **Assertion:** The created task survives server restarts and remains intact on disk.

---

### T2 - Stage 3: Update & Delete via SQL

#### Test 3.1: Partial Update via Parameterized SQL (`PUT /tasks/1`)
```bash
curl -i -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```
- **Assertion:** Returns `HTTP 200 OK`, updates row directly in SQLite.

#### Test 3.2: Delete Task via SQL (`DELETE /tasks/{id}`)
```bash
curl -i -X DELETE http://localhost:8000/tasks/1
```
- **Assertion:** Returns `HTTP 204 No Content` with empty body. Subsequent `GET /tasks/1` returns `404`.

---

### T2 - Stage 4: Direct SQL Exploration in CLI
Launch SQLite CLI in table mode:
```bash
sqlite3 database/tasks.db
.mode table
SELECT * FROM tasks;
SELECT * FROM tasks WHERE done = 1;
SELECT COUNT(*) FROM tasks;
UPDATE tasks SET done = 1 WHERE id = 2;
DELETE FROM tasks WHERE id = 3;
.exit
```
- **Assertion:** Changes reflect instantly in both SQLite shell and subsequent API queries without needing a server restart.

---

### T2 - Stage 5: Clean Clone & Self-Healing Verification
Verify that deleting `database/tasks.db` allows the application to cleanly regenerate schemas on next boot.

### T2 - Stage 6: AI vs Me Migration Diff
Compare `backend/task2_main.py` against `ai-version/task2_main.py`.

### T2 - Extras: Filter, Search, Sort & Statistics
```bash
# Filter by completion status:
curl -i "http://localhost:8000/tasks?done=true"

# Search by keyword:
curl -i "http://localhost:8000/tasks?search=SQLite"

# Case-insensitive sorting:
curl -i "http://localhost:8000/tasks?sort=title"

# Aggregate statistics:
curl -i http://localhost:8000/stats
```

---

## Task 3: Containerized PostgreSQL & Docker Stack (T3)

### T3 - Stage 0: Postgres in Docker & Secret Exclusion

#### Test 0.1: Docker CLI & Container Liveness
```bash
docker ps
```
- **Assertion:** Container `taskdb` is running on port `5432`.

#### Test 0.2: Secret Protection
```bash
git check-ignore -v .env
```
- **Assertion:** `.env` is properly excluded by `.gitignore`.

---

### T3 - Stage 1: Connect via .env & Table Seeding

#### Test 1.1: Driver & Dependency Installation
```bash
python3 -c "import psycopg; print('psycopg3 ready!')"
```
- **Assertion:** Exits 0 and prints confirmation.

#### Test 1.2: Database Inspection Inside Container
```bash
docker compose exec db bash -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\dt" -c "SELECT * FROM tasks;"'
```
- **Assertion:** Table `tasks` exists with `SERIAL PRIMARY KEY` and seeded rows.

---

### T3 - Stage 2: Read from Postgres

#### Test 2.1: Fetch All Tasks from Postgres
```bash
curl -i http://localhost:8000/tasks
```
- **Assertion:** Returns `HTTP 200 OK` reading live records from PostgreSQL.

#### Test 2.2: Fetch Single Task by ID
```bash
curl -i http://localhost:8000/tasks/1
```
- **Assertion:** Returns `HTTP 200 OK` with task 1.

---

### T3 - Stage 3: Full CRUD Operations in SQL
Verify `POST`, `PUT`, `DELETE` execute parameterized `%s` queries against PostgreSQL, returning proper status codes (`201`, `200`, `204`, `400`, `404`).

---

### T3 - Stage 4: Docker Compose Full Stack Orchestration

#### Test 4.1: Single-Command Stack Build & Liveness
```bash
docker compose up --build -d
docker compose ps
```
- **Assertion:** Both `api` and `db` services are healthy.

#### Test 4.2: Volume Persistence Across Full Teardown
```bash
# 1. Create a task
curl -s -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title": "Persistent Docker Task"}'

# 2. Tear down the entire stack (retaining volume)
docker compose down

# 3. Bring stack back up
docker compose up -d

# 4. Verify task still exists
curl -s http://localhost:8000/tasks | grep "Persistent Docker Task"
```
- **Assertion:** Task persists safely inside Docker named volume `taskdata`.

---

### T3 - Stage 5: One-Command Boot & Clean Clone Round-Trip
Verify that any fresh environment can run `docker compose up --build` with `.env` and immediately pass tests.

---

### T3 - Stage 6: AI vs Me Containerized Stack
Run and audit the isolated AI container stack:
```bash
docker compose -f ai-version/compose.yaml --env-file .env up --build -d
curl -i http://localhost:8001/health
curl -i http://localhost:8001/tasks
docker compose -f ai-version/compose.yaml --env-file .env down
```

---

## Task 4: Supabase Authentication & Cloud API Tests (T4)

### T4 - Stage 0: Setup Supabase SDK & Connection Lifecycle

#### Check 0.1: Secret Protection (.gitignore)
```bash
git check-ignore -v .env
```
- **Assertion:** Returns `.gitignore:4:.env`.

#### Check 0.2: Supabase SDK Dependency Check
```bash
python3 -c "import supabase, dotenv; print('Supabase SDK ready!')"
```
- **Assertion:** Prints `Supabase SDK ready!` with exit code 0.

#### Check 0.3: Server Startup & Lifespan Connection Log
```bash
uv run fastapi dev backend/main.py
```
- **Terminal output assertion:**
  ```text
  🚀 Server running and connected to Supabase
  INFO:     Application startup complete.
  ```

---

### T4 - Stage 1: User Registration & Token Issuance

#### Test 1.1: User Registration Check (`POST /auth/signup` -> 201 Created)
```bash
curl -i -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"stage1_test@example.com","password":"password123"}'
```
- **Assertion:** Returns `HTTP/1.1 201 Created` with Supabase user object (`id`, `email`, `created_at`).

#### Test 1.2: Authentication & Token Issuance Check (`POST /auth/login` -> 200 OK)
```bash
curl -i -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"stage1_test@example.com","password":"password123"}'
```
- **Assertion:** Returns `HTTP/1.1 200 OK` containing `"access_token"`, `"refresh_token"`, and `"token_type": "bearer"`.

#### Test 1.3: Zero-Trust Validation Check (`POST /auth/signup` -> 400 Bad Request)
```bash
# A. Missing password field
curl -i -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'

# B. Blank whitespace password
curl -i -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"   "}'
```
- **Assertion:** Returns `HTTP/1.1 400 Bad Request` with `{"error": "Email and password are required"}`.

#### Test 1.4: Invalid Credentials Rejection (`POST /auth/login` -> 401 Unauthorized)
```bash
curl -i -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"stage1_test@example.com","password":"wrongpassword"}'
```
- **Assertion:** Returns `HTTP/1.1 401 Unauthorized` with `{"error": "Invalid login credentials"}`.

---

### T4 - Stage 2: Public vs Protected Gate Extraction

#### Test 2.1: Public Route Access (`GET /public/info` -> 200 OK)
```bash
curl -i http://localhost:8000/public/info
```
- **Assertion:** Returns `HTTP/1.1 200 OK` with `{"message": "Welcome stranger! This info is public."}`.

#### Test 2.2: Protected Route Without Token (`GET /protected/profile` -> 401 Unauthorized)
```bash
curl -i http://localhost:8000/protected/profile
```
- **Assertion:** Returns `HTTP/1.1 401 Unauthorized` with `{"error": "Access token required"}`.

#### Test 2.3: Protected Route With Malformed Header (`GET /protected/profile` -> 401 Unauthorized)
```bash
curl -i http://localhost:8000/protected/profile -H "Authorization: Basic 12345"
curl -i http://localhost:8000/protected/profile -H "Authorization: Bearer "
```
- **Assertion:** Returns `HTTP/1.1 401 Unauthorized` with `{"error": "Access token required"}`.

---

### T4 - Stage 3: Cryptographic Token Verification Guard

#### Test 3.1: Valid JWT Token Verification (`GET /protected/profile` -> 200 OK)
```bash
# 1. Acquire authentic JWT
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"stage1_test@example.com","password":"password123"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# 2. Present token to protected gate
curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer $TOKEN"
```
- **Assertion:** Returns `HTTP/1.1 200 OK` with verified profile metadata (`id`, `email`, `created_at`).

#### Test 3.2: Cryptographic Tamper Rejection (`GET /protected/profile` -> 401 Unauthorized)
```bash
# Modify signature bytes
curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer ${TOKEN%????}xxxx"
```
- **Assertion:** Returns `HTTP/1.1 401 Unauthorized` with `{"error": "Invalid or expired token"}`.

---

### T4 - Stage 4: Reusable Dependency & Session Termination

#### Test 4.1: Reusable Middleware Route Access (`GET /protected/dashboard` -> 200 OK)
```bash
curl -i http://localhost:8000/protected/dashboard \
  -H "Authorization: Bearer $TOKEN"
```
- **Assertion:** Returns `HTTP/1.1 200 OK` with `"message": "Welcome to your private dashboard, stage1_test@example.com!"` and `"user_id"`.

#### Test 4.2: Session Termination / Logout (`POST /auth/logout` -> 204 No Content)
```bash
curl -i -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```
- **Assertion:** Returns `HTTP/1.1 204 No Content` with an empty response body (`Content-Length: 0`).

---

### T4 - Stage 5: Interactive Swagger UI Bearer Security

#### Test 5.1: Swagger UI Documentation Liveness
1. Open `http://localhost:8000/docs` in your browser.
2. Confirm the green **"Authorize" 🔓** button is visible.
3. Confirm lock padlocks appear beside `GET /protected/profile`, `GET /protected/dashboard`, and `POST /auth/logout`.

#### Test 5.2: In-Browser Authentication & Execution
1. Obtain an access token using `POST /auth/login`.
2. Click **Authorize 🔓** in the top-right corner of Swagger UI.
3. Paste the token into the value input and click **Authorize**.
4. Execute `GET /protected/profile` directly from Swagger UI → Returns `HTTP 200 OK`.

---

### T4 - Stage 6: Live Production Cloud Deployment

Test against the live production deployment hosted on **FastAPI Cloud**:

#### Test 6.1: Live Cloud Health & Discovery Check
```bash
# Health probe
curl -i https://crud-api-2b23f883.fastapicloud.dev/health
# Assertion: HTTP/2 200 OK -> {"status": "ok"}

# Public info endpoint
curl -i https://crud-api-2b23f883.fastapicloud.dev/public/info
# Assertion: HTTP/2 200 OK -> {"message": "Welcome stranger! This info is public."}

# OpenAPI Schema title check
curl -s https://crud-api-2b23f883.fastapicloud.dev/openapi.json | grep -o "Task 4: Auth API (Supabase + FastAPI)"
```

#### Test 6.2: Production Gate & Security Enforcement
```bash
curl -i https://crud-api-2b23f883.fastapicloud.dev/protected/profile
```
- **Assertion:** Returns `HTTP/2 401 Unauthorized` with `{"error": "Access token required"}`.

#### Test 6.3: Production Interactive Documentation Check
Navigate to [`https://crud-api-2b23f883.fastapicloud.dev/docs`](https://crud-api-2b23f883.fastapicloud.dev/docs) in your browser and confirm all 5 Auth endpoints and the Authorize padlock are functional in production.

---

## Automated Regression Suites & Runners

### 1. Shared Contract Test Suite (`pytest`)
To prove that storage is an implementation detail and that the external HTTP contract never regressed between Task 1 (in-memory) and Task 2 (SQLite):

```bash
uv run pytest -v
```

All contract tests validate:
- Root service discovery (`GET /`)
- Health monitoring (`GET /health`)
- Listing tasks with consistent shape (`GET /tasks`)
- 404 error semantics for missing tasks
- 400 validation for empty payloads
- Creation, update, and deletion lifecycles (`201`, `200`, `204`)
- SQLite-specific features (seeding idempotency, persistence across restarts, schema migration)

---

### 2. One-Click Terminal Verification Script

Save this script or run it directly in your terminal to automatically audit all core HTTP and database contracts:

```bash
bash -c '
echo "============================================="
echo "   RUNNING AUTOMATED TEST SUITE (T1, T2 & T4) "
echo "============================================="

# 1. Health Probe
echo -n "[Probe] GET /health (HTTP 200): "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
[ "$STATUS" = "200" ] && echo "✅ PASS" || echo "❌ FAIL (Got $STATUS - Is server running?)"

# 2. Public Route Check
echo -n "[Auth]  GET /public/info (HTTP 200): "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/public/info)
[ "$STATUS" = "200" ] && echo "✅ PASS" || echo "❌ FAIL (Got $STATUS)"

# 3. Protected Route Security Gate (Must be 401 without token)
echo -n "[Auth]  GET /protected/profile (HTTP 401): "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/protected/profile)
[ "$STATUS" = "401" ] && echo "✅ PASS" || echo "❌ FAIL (Got $STATUS)"

# 4. Zero-Trust Validation (Must be 400 on empty body)
echo -n "[Auth]  POST /auth/signup {} (HTTP 400): "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/auth/signup -H "Content-Type: application/json" -d "{}")
[ "$STATUS" = "400" ] && echo "✅ PASS" || echo "❌ FAIL (Got $STATUS)"

echo "============================================="
echo "               TESTS COMPLETE                "
echo "============================================="
'
```
