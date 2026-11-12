# 🧪 Test Execution Manual (T1, T2 & T3)

Comprehensive testing guide and verification checkpoints for **Task 1** (*In-Memory CRUD API*), **Task 2** (*SQLite Database CRUD API*), and **Task 3** (*Containerized PostgreSQL & Docker*).

---

## Table of Contents

- [Server Startup & Environment](#server-startup--environment)
- [Task 1: In-Memory CRUD API Tests (T1)](#task-1-in-memory-crud-api-tests-t1)
  - [Stage 0: Base Server Liveness](#t1---stage-0-base-server-liveness)
  - [Stage 1: Service Discovery & Health Check](#t1---stage-1-service-discovery--health-check)
  - [Stage 2: Read Operations](#t1---stage-2-read-operations)
  - [Stage 3: Create with Zero-Trust Validation](#t1---stage-3-create-with-zero-trust-validation)
  - [Stage 4: Update & Delete Operations](#t1---stage-4-update--delete-operations)
  - [Stage 5: Swagger UI Audit](#t1---stage-5-swagger-ui-audit)
  - [Stage 6: Git Delivery Audit](#t1---stage-6-git-delivery-audit)
  - [Stage 7: AI Rematch Diff](#t1---stage-7-ai-rematch-diff)
- [Task 2: SQLite Database CRUD API Tests (T2)](#task-2-sqlite-database-crud-api-tests-t2)
  - [Stage 0: Database & Lifecycle Setup (Complete)](#t2---stage-0-database--lifecycle-setup-complete)
  - [Stage 1: Read from SQLite (Complete)](#t2---stage-1-read-from-sqlite-complete)
  - [Stage 2: Create in SQLite (Complete)](#t2---stage-2-create-in-sqlite-complete)
  - [Stage 3: Update & Delete via SQL (Complete)](#t2---stage-3-update--delete-via-sql-complete)
  - [Stage 4: Direct SQL Exploration by Hand (Complete)](#t2---stage-4-direct-sql-exploration-by-hand-complete)
  - [Stage 5: Clean Clone & Documentation (Complete)](#t2---stage-5-clean-clone--documentation-complete)
  - [Stage 6: AI vs Me Migration Diff (Complete)](#t2---stage-6-ai-vs-me-migration-diff-complete)
- [Task 3: Containerized PostgreSQL & Docker (T3)](#task-3-containerized-postgresql--docker-t3)
  - [Stage 0: Postgres in Docker & gitignore (Complete)](#t3---stage-0-postgres-in-docker--gitignore-complete)
  - [Stage 1: Connect via .env & Create Table (Complete)](#t3---stage-1-connect-via-env--create-table-complete)
  - [Stage 2: Read from Postgres (Upcoming)](#t3---stage-2-read-from-postgres-upcoming)
  - [Stage 3: Full CRUD on Postgres (Upcoming)](#t3---stage-3-full-crud-on-postgres-upcoming)
  - [Stage 4: Docker Compose the Whole Stack (Upcoming)](#t3---stage-4-docker-compose-the-whole-stack-upcoming)
  - [Stage 5: One-Command Stack & Docs (Upcoming)](#t3---stage-5-one-command-stack--docs-upcoming)
  - [Stage 6: AI Rematch (Upcoming)](#t3---stage-6-ai-rematch-upcoming)
- [One-Click Automated Test Runner](#one-click-automated-test-runner)

---

## Server Startup & Environment

Ensure you are at the repository root (`CRUD_API`):

```bash
# Run Task 2 (SQLite Database API - Default):
fastapi dev
# OR: uv run fastapi dev

# Run Task 1 (In-Memory API):
fastapi dev backend/task1_main.py
# OR: uv run fastapi dev backend/task1_main.py
```

- **Base URL:** `http://localhost:8000`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## Task 1: In-Memory CRUD API Tests (T1)

### T1 - Stage 0: Base Server Liveness
Verify that the ASGI server boots and accepts incoming TCP connections.

```bash
curl -i http://localhost:8000/
```
- **Expected Status:** `200 OK`
- **Expected Body:** JSON describing API metadata.

---

### T1 - Stage 1: Service Discovery & Health Check

#### 1. Root Service Discovery (`GET /`)
```bash
curl -s http://localhost:8000/ | jq .
```
**Expected Response:**
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
**Expected Response:**
```http
HTTP/1.1 200 OK
content-type: application/json

{"status":"ok"}
```

---

### T1 - Stage 2: Read Operations

#### 1. Fetch All Tasks (`GET /tasks`)
```bash
curl -i http://localhost:8000/tasks
```
- **Expected Status:** `200 OK`
- **Expected Response:** JSON array containing tasks.

#### 2. Lookup Valid Task ID (`GET /tasks/1`)
```bash
curl -i http://localhost:8000/tasks/1
```
- **Expected Status:** `200 OK`
- **Expected Response:** Single task object matching ID 1.

#### 3. Lookup Non-Existent Task ID (`GET /tasks/999`)
```bash
curl -i http://localhost:8000/tasks/999
```
- **Expected Status:** `404 Not Found`
- **Expected Response:** `{"detail":"Task 999 not found"}`

---

### T1 - Stage 3: Create with Zero-Trust Validation

#### 1. Successful Task Creation (`POST /tasks`)
```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Implement automated regression suite"}'
```
- **Expected Status:** `201 Created`
- **Expected Response:**
  ```json
  {
    "id": 5,
    "title": "Implement automated regression suite",
    "done": false
  }
  ```

#### 2. Validation: Empty Payload (`POST /tasks`)
```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{}'
```
- **Expected Status:** `400 Bad Request`
- **Expected Response:** `{"detail":"Title is required and cannot be empty"}`

#### 3. Validation: Whitespace Only (`POST /tasks`)
```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "     "}'
```
- **Expected Status:** `400 Bad Request`
- **Expected Response:** `{"detail":"Title is required and cannot be empty"}`

---

### T1 - Stage 4: Update & Delete Operations

#### 1. Partial Update: Mark Task Done (`PUT /tasks/1`)
```bash
curl -i -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```
- **Expected Status:** `200 OK`
- **Expected Response:** Updated task object with `"done": true`.

#### 2. Partial Update: Change Title (`PUT /tasks/1`)
```bash
curl -i -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title Name"}'
```
- **Expected Status:** `200 OK`
- **Expected Response:** Updated task object with new title.

#### 3. Update Validation: Empty Body (`PUT /tasks/1`)
```bash
curl -i -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{}'
```
- **Expected Status:** `400 Bad Request`
- **Expected Response:** `{"detail":"Must provide title or done to update"}`

#### 4. Update Unknown ID (`PUT /tasks/999`)
```bash
curl -i -X PUT http://localhost:8000/tasks/999 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```
- **Expected Status:** `404 Not Found`
- **Expected Response:** `{"detail":"Task 999 not found"}`

#### 5. Delete Task (`DELETE /tasks/1`)
```bash
curl -i -X DELETE http://localhost:8000/tasks/1
```
- **Expected Status:** `204 No Content`
- **Expected Response Body:** *Empty body (0 bytes)*.

#### 6. Delete Verification: Deleted ID Returns 404 (`DELETE /tasks/1`)
```bash
curl -i -X DELETE http://localhost:8000/tasks/1
```
- **Expected Status:** `404 Not Found`
- **Expected Response:** `{"detail":"Task 1 not found"}`

---

### T1 - Stage 5: Swagger UI Audit
Open browser to `http://localhost:8000/docs`:
- Verify all 5 routes are present: `GET /`, `GET /health`, `GET /tasks`, `POST /tasks`, `PUT /tasks/{task_id}`, `DELETE /tasks/{task_id}`.
- Test "Try it out" button for `POST /tasks` and verify HTTP 201 response.

---

### T1 - Stage 6: Git Delivery Audit
Verify honest commit milestone history:

```bash
git log --oneline -n 8
```
- Confirm discrete commits corresponding to each stage.

---

### T1 - Stage 7: AI Rematch Diff
Compare hand-crafted code with quarantined AI code:

```bash
git diff --no-index backend/main.py ai-version/main.py
```
- Review differences in routing, types, validation, and docstring structure.

---

## Task 2: SQLite Database CRUD API Tests (T2)

### T2 - Stage 0: Database & Lifecycle Setup (Complete)

#### Test 0.1: SQLite File & Table Schema Verification
Run directly from terminal without needing the server:

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('database/tasks.db')
cursor = conn.cursor()

# Verify table definition
cursor.execute(\"SELECT sql FROM sqlite_master WHERE type='table' AND name='tasks'\")
print('Table DDL:\n', cursor.fetchone()[0])

# Verify row count and seeded content
cursor.execute('SELECT id, title, done FROM tasks')
rows = cursor.fetchall()
print(f'\nTotal rows: {len(rows)}')
for row in rows:
    print(f'Row {row[0]}: title=\"{row[1]}\", done={row[2]}')
"
```
**Expected Output:**
```text
Table DDL:
 CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
)

Total rows: 3
Row 1: title="Task 1: Build CRUD API with in-memory storage", done=1
Row 2: title="Task 2: Connect CRUD API to SQLite database", done=1
Row 3: title="Task 3: Containerise the project stack with Docker", done=0
```

#### Test 0.2: Idempotent Seeding & Restart Test
Proves that tasks do **not duplicate** when the application boots repeatedly:

1. Note the current row count:
   ```bash
   python3 -c "import sqlite3; conn = sqlite3.connect('database/tasks.db'); print('Count before:', conn.cursor().execute('SELECT COUNT(*) FROM tasks').fetchone()[0])"
   ```
2. Start the server (`fastapi dev`), then stop it with `Ctrl+C`. Repeat 3 times.
3. Check the count again:
   ```bash
   python3 -c "import sqlite3; conn = sqlite3.connect('database/tasks.db'); print('Count after 3 restarts:', conn.cursor().execute('SELECT COUNT(*) FROM tasks').fetchone()[0])"
   ```
- **Assertion:** The count must remain **identical** before and after (e.g., `3 == 3`).

#### Test 0.3: Clean Clone / Self-Healing Test
Proves that a fresh clone provides a working database with zero manual setup:

```bash
# 1. Delete the database file
rm database/tasks.db

# 2. Start the server briefly to trigger lifespan
fastapi dev &
SERVER_PID=$!
sleep 2
kill $SERVER_PID

# 3. Confirm the database file and seeded tasks were recreated automatically
python3 -c "
import sqlite3
conn = sqlite3.connect('database/tasks.db')
print('Auto-created row count:', conn.cursor().execute('SELECT COUNT(*) FROM tasks').fetchone()[0])
"
```
- **Assertion:** Prints `Auto-created row count: 3`.

---

### T2 - Stage 1: Read from SQLite (Complete)

Verify that `GET /tasks` and `GET /tasks/{id}` read live from `database/tasks.db` using SQL queries (`SELECT id, title, done FROM tasks` and `SELECT ... WHERE id = ?`).

#### Test 1.1: Fetch All Tasks from SQLite (`GET /tasks`)
```bash
curl -i http://localhost:8000/tasks
```
- **Expected Status:** `200 OK`
- **Expected Response:** JSON array with all tasks and boolean `"done"` status:
  ```json
  [
    {"id": 1, "title": "Task 1: Build CRUD API with in-memory storage", "done": true},
    {"id": 2, "title": "Task 2: Connect CRUD API to SQLite database", "done": false}
  ]
  ```

#### Test 1.2: Fetch Single Task (`GET /tasks/1`)
```bash
curl -i http://localhost:8000/tasks/1
```
- **Expected Status:** `200 OK`
- **Expected Response:**
  ```json
  {"id": 1, "title": "Task 1: Build CRUD API with in-memory storage", "done": true}
  ```

#### Test 1.3: Fetch Non-Existent Task (`GET /tasks/999`)
```bash
curl -i http://localhost:8000/tasks/999
```
- **Expected Status:** `404 Not Found`
- **Expected Response:** `{"error":"Task not found"}`

---

### T2 - Stage 2: Create in SQLite (Complete)

Verify that new tasks are saved permanently to `database/tasks.db` using `INSERT INTO tasks (title, done) VALUES (?, ?)`.

#### Test 2.1: Successful Task Creation (`POST /tasks`)
```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test persistent database storage"}'
```
- **Expected Status:** `201 Created`
- **Expected Response:** Auto-assigned database primary key and `done: false`:
  ```json
  {
    "id": 3,
    "title": "Test persistent database storage",
    "done": false
  }
  ```

#### Test 2.2: Zero-Trust Validation - Missing/Empty Title
```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{}'
```
- **Expected Status:** `400 Bad Request`
- **Expected Response:** `{"error":"Title is required and cannot be empty"}`

#### Test 2.3: Zero-Trust Validation - Whitespace-Only Title
```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "     "}'
```
- **Expected Status:** `400 Bad Request`
- **Expected Response:** `{"error":"Title is required and cannot be empty"}`

#### Test 2.4: THE RESTART TEST (Data Persistence Proof)
This test proves that the data outlives program memory:

1. Create a task via API:
   ```bash
   curl -i -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "I will survive server restarts"}'
   ```
2. Stop the server by pressing `Ctrl + C` in the server terminal.
3. Start the server again:
   ```bash
   fastapi dev
   ```
4. Query the tasks:
   ```bash
   curl -s http://localhost:8000/tasks | jq .
   ```
- **Assertion:** `"I will survive server restarts"` is **still in the output**!

---

### T2 - Stage 3: Update & Delete via SQL (Complete)

Verify that `PUT` and `DELETE` execute parameterized SQL queries directly against `database/tasks.db` (`UPDATE tasks SET ...` and `DELETE FROM tasks ...`).

#### Test 3.1: Partial Update - Change Completion Status (`PUT /tasks/1`)
```bash
curl -i -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done": false}'
```
- **Expected Status:** `200 OK`
- **Expected Response:** Task with `"done": false`:
  ```json
  {"id": 1, "title": "Task 1: Build CRUD API with in-memory storage", "done": false}
  ```

#### Test 3.2: Partial Update - Change Title (`PUT /tasks/1`)
```bash
curl -i -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Task 1 Title"}'
```
- **Expected Status:** `200 OK`
- **Expected Response:** Task with updated title.

#### Test 3.3: Update Validation - Empty Body (`PUT /tasks/1`)
```bash
curl -i -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{}'
```
- **Expected Status:** `400 Bad Request`
- **Expected Response:** `{"error":"At least one field (title or done) must be provided"}`

#### Test 3.4: Update Validation - Whitespace Title (`PUT /tasks/1`)
```bash
curl -i -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "   "}'
```
- **Expected Status:** `400 Bad Request`
- **Expected Response:** `{"error":"Title cannot be empty or whitespace"}`

#### Test 3.5: Update Non-Existent ID (`PUT /tasks/999`)
```bash
curl -i -X PUT http://localhost:8000/tasks/999 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```
- **Expected Status:** `404 Not Found`
- **Expected Response:** `{"error":"Task not found"}`

#### Test 3.6: Delete Task (`DELETE /tasks/{id}`)
```bash
# 1. Create a disposable task to delete
DISPOSABLE_ID=$(curl -s -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Temporary Task for Deletion"}' | jq .id)

# 2. Delete it from SQLite
curl -i -X DELETE http://localhost:8000/tasks/$DISPOSABLE_ID
```
- **Expected Status:** `204 No Content`
- **Expected Response Body:** *Empty body (0 bytes)*.

#### Test 3.7: Delete Non-Existent ID (`DELETE /tasks/999`)
```bash
curl -i -X DELETE http://localhost:8000/tasks/999
```
- **Expected Status:** `404 Not Found`
- **Expected Response:** `{"error":"Task not found"}`

#### Test 3.8: Direct Database Verification
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('database/tasks.db')
cursor = conn.cursor()
cursor.execute('SELECT id FROM tasks WHERE id = 999')
assert cursor.fetchone() is None
print('Task 999 verified absent in SQLite database: True')
"
```

#### Test 3.9: Full CRUD Lifecycle Across Restarts
Execute the complete sequence to verify state holding:
1. `POST /tasks` -> Save new task.
2. `PUT /tasks/{id}` -> Mark task done.
3. Stop server (`Ctrl + C`), restart with `fastapi dev`.
4. `GET /tasks/{id}` -> Verify state held across the restart.
5. `DELETE /tasks/{id}` -> Remove task.
6. `GET /tasks/{id}` -> Confirm HTTP 404.

---

### T2 - Stage 4: Direct SQL Exploration by Hand (Complete)

Directly execute queries against `database/tasks.db` using the `sqlite3` CLI or DB Browser for SQLite:

```bash
# Launch interactive SQLite shell
sqlite3 database/tasks.db

# Enable pretty table output:
.mode table
.headers on

# 1. Retrieve all tasks
SELECT * FROM tasks;

# 2. Filter completed tasks
SELECT * FROM tasks WHERE done = 1;

# 3. Count total tasks
SELECT COUNT(*) FROM tasks;

# 4. Direct update in database
UPDATE tasks SET done = 1 WHERE id = 2;

# 5. Direct delete in database
DELETE FROM tasks WHERE id = 3;

# Exit shell
.quit
```

#### Test 4.1: Instant API Reflection Check (No Server Restart)
1. Run direct SQL update:
   ```bash
   sqlite3 database/tasks.db "UPDATE tasks SET title = 'Verified Direct Update', done = 1 WHERE id = 1;"
   ```
2. Immediately curl the running API:
   ```bash
   curl -s http://localhost:8000/tasks/1 | jq .
   ```
- **Assertion:** API immediately returns `"title": "Verified Direct Update"` without restarting the server, proving that `tasks.db` is the shared single source of truth.

---

### T2 - Stage 5: Clean Clone & Documentation (Complete)

Validate the **"Clean Clone / Stranger Test"** — proving that a developer who clones the repository from scratch can run the single documented start command without manual configuration:

#### Test 5.1: Clean Clone Database Auto-Creation Checkpoint
1. **Stop any active server instance** (`Ctrl + C`).
2. **Remove the database file** to simulate a fresh clone:
   ```bash
   rm -f database/tasks.db
   ```
3. **Execute the single documented start command**:
   ```bash
   fastapi dev
   # OR: uv run fastapi dev
   ```
4. **Verify startup logs**:
   ```text
   Starting application: Initializing database...
   ✅ Database initialized and seeded with 3 tasks.
   INFO:     Application startup complete.
   ```
5. **Probe the API endpoint via cURL**:
   ```bash
   curl -i http://localhost:8000/tasks
   ```
- **Assertion:** 
  - Status code `200 OK`.
  - Body contains the seeded default tasks with IDs 1, 2 and 3.
  - `database/tasks.db` was created automatically on disk.
  - Repeating server restarts does not duplicate seed rows (`SELECT COUNT(*) FROM tasks` stays consistent).

---

### T2 - Stage 6: AI vs Me Migration Diff (Complete)
```bash
# Run the quarantined AI version on a separate port (uses ai-version/tasks.db)
uv run fastapi dev ai-version/main.py --port 8001
# Diff storage code against the hand-built version
git diff --no-index backend/main.py ai-version/main.py
```
- Re-run the Stage 2 and Stage 3 checkpoints against port 8001, restart it, and confirm seeds are not duplicated and data persists.
- Task 1 AI version now lives at `ai-version/task1_main.py` (`git diff --no-index backend/task1_main.py ai-version/task1_main.py`).

---

### T2 - Extras & Automated Tests
```bash
uv run pytest -v                                   # shared Task 1/Task 2 contract tests + SQLite tests
curl -i "http://localhost:8000/tasks?done=true"    # only completed tasks
curl -i "http://localhost:8000/tasks?search=CRUD"  # LIKE search
curl -i "http://localhost:8000/tasks?sort=title"   # ORDER BY title
curl -i http://localhost:8000/stats                # {"total":3,"done":2,"pending":1} on a fresh db
```

---

## Task 3: Containerized PostgreSQL & Docker (T3)

Testing guide and verification checkpoints for the containerized PostgreSQL stack in Docker.

### T3 - Stage 0: Postgres in Docker & gitignore (Complete)

Verify that PostgreSQL 16 is running inside an isolated Docker container with a persistent volume:

#### Test 0.1: Docker CLI Liveness Check
```bash
docker --version
```
- **Assertion:** Prints `Docker version ...` confirming the Docker CLI is available on `$PATH`.

#### Test 0.2: Container Liveness Check
```bash
docker ps
```
- **Assertion:** `taskdb` container is listed with `STATUS: Up ...` and port mapping `0.0.0.0:5432->5432/tcp`.

#### Test 0.3: SQL Prompt Interactive Check
```bash
docker exec -it taskdb psql -U postgres -d tasks
```
- Inside the PostgreSQL interactive shell:
  - Run `\dt` -> Expect `Did not find any relations.` (clean database initialized).
  - Run `\q` -> Successfully exits shell back to terminal.

#### Test 0.4: Secret Protection (.gitignore)
```bash
git check-ignore -v .env
```
- **Assertion:** Returns `.gitignore:4:.env`, verifying that `.env` is ignored by Git to protect secrets.

---

### T3 - Stage 1: Connect via .env & Create Table (Complete)

Verify that the FastAPI application connects to containerized PostgreSQL using secrets from `.env` and automatically initializes the `tasks` schema and seed data on startup:

#### Test 1.1: Driver & Dependency Installation Check
```bash
python3 -c "import psycopg, dotenv; print('Dependencies ready!')"
```
- **Assertion:** Prints `Dependencies ready!` without import errors.

#### Test 1.2: Startup Auto-Creation & Seeding
1. Start the FastAPI development server:
   ```bash
   fastapi dev
   ```
2. Check terminal startup logs:
   ```text
   Starting application: Initializing PostgreSQL database...
   ✅ PostgreSQL database initialized and seeded with 3 tasks.
   INFO:     Application startup complete.
   ```

#### Test 1.3: PostgreSQL Schema & Table Check
In another terminal, inspect the containerized PostgreSQL database directly:
```bash
docker exec -it taskdb psql -U postgres -d tasks -c "\dt"
```
- **Assertion:** Lists `public | tasks | table | postgres`.

#### Test 1.4: PostgreSQL Seed Verification Check
```bash
docker exec -it taskdb psql -U postgres -d tasks -c "SELECT id, title, done FROM tasks;"
```
- **Assertion:** Displays 3 rows:
  - `1 | Task 1: Build CRUD API with in-memory storage | t`
  - `2 | Task 2: Connect CRUD API to SQLite database | t`
  - `3 | Task 3: Containerise the project stack with Docker | f`

#### Test 1.5: Idempotency Check (Restart 3 Times)
Restart the server 3 times (`Ctrl + C`, then `fastapi dev`) and re-run:
```bash
docker exec -it taskdb psql -U postgres -d tasks -c "SELECT COUNT(*) FROM tasks;"
```
- **Assertion:** Count remains strictly `3` (seeds never duplicate).

---

## One-Click Automated Test Runner

Save the following test runner or execute it directly in terminal to validate the active server and database state:

```bash
bash -c '
echo "============================================="
echo "   RUNNING AUTOMATED TEST SUITE (T1 & T2)   "
echo "============================================="

# 1. Database File & Schema Check
echo -n "[T2-0.1] Database Schema Check: "
python3 -c "
import sqlite3
conn = sqlite3.connect(\"database/tasks.db\")
c = conn.cursor()
c.execute(\"SELECT name FROM sqlite_master WHERE type=\x27table\x27 AND name=\x27tasks\x27\")
assert c.fetchone() is not None
" && echo "✅ PASS" || echo "❌ FAIL"

# 2. Database Seed Count Check
echo -n "[T2-0.2] Seeded Row Count Check: "
python3 -c "
import sqlite3
conn = sqlite3.connect(\"database/tasks.db\")
c = conn.cursor()
count = c.execute(\"SELECT COUNT(*) FROM tasks\").fetchone()[0]
assert count >= 2, f\"Expected >= 2 rows, found {count}\"
" && echo "✅ PASS" || echo "❌ FAIL"

# 3. HTTP Health Probe
echo -n "[T1-1.1] GET /health (HTTP 200): "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
[ "$STATUS" = "200" ] && echo "✅ PASS" || echo "❌ FAIL (Got $STATUS - Is server running?)"

# 4. HTTP Root Discovery
echo -n "[T1-1.2] GET / (HTTP 200): "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
[ "$STATUS" = "200" ] && echo "✅ PASS" || echo "❌ FAIL (Got $STATUS)"

# 5. HTTP Validation Check (400 on empty payload)
echo -n "[T1-3.2] POST /tasks {} (HTTP 400): "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{}")
[ "$STATUS" = "400" ] && echo "✅ PASS" || echo "❌ FAIL (Got $STATUS)"

# 6. HTTP 404 Check
echo -n "[T2-1.3] GET /tasks/9999 (HTTP 404): "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/tasks/9999)
[ "$STATUS" = "404" ] && echo "✅ PASS" || echo "❌ FAIL (Got $STATUS)"

# 7. Persistent Task Creation Check
echo -n "[T2-2.1] POST /tasks (HTTP 201 Created): "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\": \"Automated Verification Task\"}")
[ "$STATUS" = "201" ] && echo "✅ PASS" || echo "❌ FAIL (Got $STATUS)"

# 8. Persistent Task Update Check
echo -n "[T2-3.1] PUT /tasks/1 (HTTP 200 OK): "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X PUT http://localhost:8000/tasks/1 -H "Content-Type: application/json" -d "{\"done\": true}")
[ "$STATUS" = "200" ] && echo "✅ PASS" || echo "❌ FAIL (Got $STATUS)"

# 9. Update Validation Check (400 on empty payload)
echo -n "[T2-3.3] PUT /tasks/1 {} (HTTP 400): "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X PUT http://localhost:8000/tasks/1 -H "Content-Type: application/json" -d "{}")
[ "$STATUS" = "400" ] && echo "✅ PASS" || echo "❌ FAIL (Got $STATUS)"

echo "============================================="
echo "               TESTS COMPLETE                "
echo "============================================="
'
```

