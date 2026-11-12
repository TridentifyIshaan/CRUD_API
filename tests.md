# 🧪 Test Execution Manual (T1 & T2)

Comprehensive testing guide and verification checkpoints for **Task 1** (*In-Memory CRUD API*) and **Task 2** (*SQLite Database CRUD API*).

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
  - [Stage 3: Update & Delete via SQL (Upcoming)](#t2---stage-3-update--delete-via-sql-upcoming)
  - [Stage 4: Parameterized Safety & SQL Injection (Upcoming)](#t2---stage-4-parameterized-safety--sql-injection-upcoming)
  - [Stage 5: Clean Clone & Documentation (Upcoming)](#t2---stage-5-clean-clone--documentation-upcoming)
  - [Stage 6: AI Rematch Migration Diff (Upcoming)](#t2---stage-6-ai-rematch-migration-diff-upcoming)
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
    done BOOLEAN NOT NULL DEFAULT 0   
)

Total rows: 2
Row 1: title="Task 1: Build your first CRUD API with in-memory storage", done=1
Row 2: title="Task 2: Connect CRUD API to SQLite database", done=0
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
- **Assertion:** The count must remain **identical** before and after (e.g., `2 == 2`).

#### Test 0.3: Clean Clone / Self-Healing Test
Proves that a stranger cloning your repo gets a working database with zero manual setup:

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
- **Assertion:** Prints `Auto-created row count: 2`.

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
    {"id": 1, "title": "Task 1: Build your first CRUD API with in-memory storage", "done": true},
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
  {"id": 1, "title": "Task 1: Build your first CRUD API with in-memory storage", "done": true}
  ```

#### Test 1.3: Fetch Non-Existent Task (`GET /tasks/999`)
```bash
curl -i http://localhost:8000/tasks/999
```
- **Expected Status:** `404 Not Found`
- **Expected Response:** `{"detail":"Task 999 not found"}`

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
- **Expected Response:** `{"detail":"Title is required & can't be empty"}`

#### Test 2.3: Zero-Trust Validation - Whitespace-Only Title
```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "     "}'
```
- **Expected Status:** `400 Bad Request`
- **Expected Response:** `{"detail":"Title is required & can't be empty"}`

#### Test 2.4: THE RESTART TEST (Data Persistence Proof)
This test proves that the data outlives program memory:

1. Create a task via API:
   ```bash
   curl -i -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "I will survive server restarts"}'
   ```
2. Stop your server by pressing `Ctrl + C` in the server terminal.
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

### T2 - Stage 3: Update & Delete via SQL (Upcoming)

When `PUT` and `DELETE` are migrated to SQL:

```bash
# 1. Update task in SQLite
curl -i -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done": false}'

# 2. Delete task from SQLite
curl -i -X DELETE http://localhost:8000/tasks/1
# Expect: 204 No Content

# 3. Verify deletion in database directly
python3 -c "
import sqlite3
conn = sqlite3.connect('database/tasks.db')
print('Task 1 exists:', conn.cursor().execute('SELECT id FROM tasks WHERE id = 1').fetchone() is not None)
"
# Expect: Task 1 exists: False
```

---

### T2 - Stage 4: Parameterized Safety & SQL Injection (Upcoming)

Proves that raw strings cannot compromise the database:

```bash
# Attempt SQL injection in title
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Clean Task\"); DROP TABLE tasks; --"}'

# Verify table still exists
python3 -c "
import sqlite3
conn = sqlite3.connect('database/tasks.db')
cursor = conn.cursor()
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'\")
print('Table survived SQL injection attempt:', cursor.fetchone() is not None)
"
```
- **Assertion:** Table survived SQL injection attempt: `True`.

---

### T2 - Stage 5: Clean Clone & Documentation (Upcoming)
Verify that README contains:
- Why SQLite was selected.
- Single command to boot the app.
- Screenshot of DB Browser for SQLite showing the `tasks` table.

---

### T2 - Stage 6: AI Rematch Migration Diff (Upcoming)
```bash
git diff --no-index backend/main.py ai-version/main.py
```
- Compare the database migration implementation against AI generated storage logic.

---

## One-Click Automated Test Runner

Save the following test runner or execute it directly in your terminal to validate the currently active server and database state:

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

echo "============================================="
echo "               TESTS COMPLETE                "
echo "============================================="
'
```

