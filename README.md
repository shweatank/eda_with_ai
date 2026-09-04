# AI-Powered RTL Verification & Debugging Platform

Verify SystemVerilog RTL automatically with **Icarus Verilog**, store the
verification graph in **Neo4j AuraDB**, and use **Groq** to explain the
failures — all driven from a **Streamlit** dashboard through a
**Strawberry GraphQL** API on **FastAPI**.

Nothing is simulated in Python: every PASS/FAIL comes from a real
`iverilog` + `vvp` run.

---

## 1. Project overview

The platform takes two small SystemVerilog designs, each with a correct
version and a version containing one deliberate RTL bug, and runs the
complete verification loop:

| Example | Passing | Failing (bug in RTL only) |
|---|---|---|
| Traffic Light Controller (FSM) | 4 passed / 0 failed | 2 passed / 2 failed |
| 4-bit ALU | 4 passed / 0 failed | 3 passed / 1 failed |

The testbench is **byte-for-byte identical** between the passing and
failing folders. Only the RTL differs, so the failure can only come from
the design.

Three separation-of-concerns rules hold throughout:

1. **The simulator decides PASS/FAIL.** The log parser reads what
   `vvp` actually printed. No verdict is hard-coded in Python.
2. **Static rules decide the failure category and severity.**
   `failure_analyzer.py` is deterministic and never calls the AI.
3. **The AI only explains.** Groq is called only when a failure already
   exists, receives evidence only, and its response model has no
   pass/fail field at all — so it structurally cannot alter a verdict.

---

## 2. Architecture

```
Streamlit  (frontend/app.py)
    |  GraphQL over HTTP (requests)
    v
GraphQL    (Strawberry: backend/graphql/)
    v
FastAPI    (backend/main.py)
    v
Verification Service  (ThreadPoolExecutor, 4 workers)
    v
Icarus Verilog  ->  iverilog -g2012 -o simulation.vvp rtl tb
    v
Simulation      ->  vvp simulation.vvp   -> simulation.log + waveform.vcd
    v
Log Parser      ->  structured Pydantic models
    v
PASS / FAIL
    v
Neo4j AuraDB    ->  Project / RTLModule / Testbench / VerificationJob /
                    Simulation / Test / Failure / Waveform / AIAnalysis
    v
If FAIL -> retrieve failure evidence -> Groq AI -> Root Cause Analysis
    v
Store AIAnalysis in Neo4j
    v
GraphQL -> Streamlit
```

Streamlit never talks to Neo4j directly. It only calls
`http://localhost:8000/graphql`.

### Layout

```
ai_rtl_debugger/
├── backend/
│   ├── main.py                     FastAPI app, /health, /graphql, lifespan
│   ├── config.py                   .env loading (no hard-coded secrets)
│   ├── database/
│   │   ├── neo4j_client.py         driver lifecycle, health, scrubbed errors
│   │   └── neo4j_schema.py         constraints + indexes, applied at startup
│   ├── graphql/
│   │   ├── schema.py               Strawberry schema
│   │   ├── queries.py              projects, project, verificationJob, ...
│   │   ├── mutations.py            createProject, runVerification
│   │   └── types.py                all *Type definitions
│   ├── services/
│   │   ├── verification_service.py orchestrator + thread pool
│   │   ├── compilation_service.py  iverilog  (subprocess, shell=False)
│   │   ├── simulation_service.py   vvp       (subprocess, shell=False)
│   │   ├── log_parser.py           simulator output -> Pydantic
│   │   ├── failure_analyzer.py     deterministic category + severity
│   │   ├── ai_service.py           Groq, evidence-only, Pydantic-validated
│   │   └── neo4j_service.py        every node/relationship, parameterised
│   └── models/schemas.py           Pydantic models
├── frontend/app.py                 Streamlit dashboard
├── verilog/
│   ├── traffic_light/{passing,failing}/
│   └── alu/{passing,failing}/
├── data/jobs/<jobId>/              simulation.vvp, simulation.log, waveform.vcd
├── tests/
│   ├── test_log_parser.py
│   └── test_failure_analyzer.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## 3. Technology stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| API | Strawberry GraphQL |
| Backend | FastAPI + Uvicorn |
| Database | Neo4j AuraDB (cloud) |
| AI | Groq |
| RTL compile/simulate | Icarus Verilog (`iverilog`, `vvp`) |
| Waveform viewer | GTKWave (optional) |
| Language | Python 3.11 (3.10 also works) |
| Background work | `concurrent.futures.ThreadPoolExecutor`, 4 workers |

No Docker, Kubernetes, Render, PostgreSQL, Redis, Kafka, Celery or vector
database. No deployment step.

---

## 4. Neo4j AuraDB setup

1. Go to <https://console.neo4j.com> and create a **free AuraDB instance**.
2. When the instance is created, **download or copy the credentials** —
   the password is shown only once.
3. Copy the connection URI, which looks like
   `neo4j+s://xxxxxxxx.databases.neo4j.io`.
4. Put the URI, username, password and database name into `.env`
   (see section 8).

You do **not** need to create a single node or constraint by hand. All
constraints and indexes are created by `backend/database/neo4j_schema.py`
when FastAPI starts, and every node and relationship is created from
Python by `backend/services/neo4j_service.py`.

> For most AuraDB instances the username and database are both `neo4j`.
> Some instances use the instance id instead — use whatever the
> credentials file you downloaded says.

---

## 5. Groq setup

1. Sign up at <https://console.groq.com>.
2. Create an API key at <https://console.groq.com/keys>.
3. Put it in `.env` as `GROQ_API_KEY`.
4. Optionally set `GROQ_MODEL` (default `openai/gpt-oss-120b`).

If `GROQ_API_KEY` is missing the platform still runs: verification
completes normally and the AI section shows a clearly labelled
`[AI unavailable]` deterministic summary instead of crashing.

---

## 6. Icarus Verilog setup

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install -y iverilog

# macOS
brew install icarus-verilog

# Windows
# install from https://bleyer.org/icarus/ and add it to PATH
```

Verify:

```bash
iverilog -V
```

Icarus Verilog **11.0 or newer** is required for `-g2012` (SystemVerilog).

---

## 7. GTKWave setup

```bash
# Ubuntu / Debian
sudo apt install -y gtkwave

# macOS
brew install --cask gtkwave
```

GTKWave is only a viewer. It is **not** part of the application runtime —
the platform generates `waveform.vcd` and the UI shows you the path and
the command to open it.

---

## 8. Environment variables

Copy the template and fill it in:

```bash
cp .env.example .env
```

`.env`:

```
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b

BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
GRAPHQL_URL=http://localhost:8000/graphql

IVERILOG_BIN=iverilog
VVP_BIN=vvp
SIM_TIMEOUT_SECONDS=60
```

`.env` is listed in `.gitignore`. No credential is ever hard-coded, and
`/health` reports only *whether* a credential is configured, never its
value.

---

## 9. Installation

```bash
cd ai_rtl_debugger

python -m venv .venv

# Linux / macOS
source .venv/bin/activate
# Windows
# .venv\Scripts\activate

pip install -r requirements.txt
```

Check the toolchain:

```bash
iverilog -V
```

Run the tests:

```bash
pytest
```

---

## 10. Running the backend

```bash
uvicorn backend.main:app --reload --port 8000
```

Check it:

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "ok",
  "neo4j": "connected",
  "groq": "configured",
  "groq_model": "openai/gpt-oss-120b",
  "iverilog": "Icarus Verilog version 11.0 (stable) ()"
}
```

GraphiQL is available in the browser at <http://localhost:8000/graphql>.

---

## 11. Running the frontend

In a **second terminal** (with the venv activated):

```bash
streamlit run frontend/app.py
```

Open <http://localhost:8501>.

---

## Demos

In the dashboard: pick the example, pick the scenario, press
**RUN VERIFICATION**. The UI polls the job every second and shows every
test — passed *and* failed.

### 12. Traffic Light PASS demo

Select **Traffic Light Controller** + **Passing**.

```
Total Tests : 4
Passed      : 4
Failed      : 0
Status      : PASSED

✓ TEST_1 — Reset     — PASS
✓ TEST_2 — A_GREEN   — PASS
✓ TEST_3 — A_YELLOW  — PASS
✓ TEST_4 — B_GREEN   — PASS
```

No Failure Details section and no AI section appear — Groq is not called
when nothing failed.

### 13. Traffic Light FAIL demo

Select **Traffic Light Controller** + **Failing**.

The bug is one line in `verilog/traffic_light/failing/traffic_light.sv`:

```systemverilog
localparam int GREEN_TICKS  = 2;   // BUG: should be 4
```

Green states end after 2 cycles instead of 4, so the FSM runs ahead of
schedule.

```
Total Tests : 4
Passed      : 2
Failed      : 2
Status      : FAILED

✓ TEST_1 — Reset     — PASS
✓ TEST_2 — A_GREEN   — PASS
✗ TEST_3 — A_YELLOW  — FAIL    expected A_YELLOW, actual B_GREEN
✗ TEST_4 — B_GREEN   — FAIL    expected B_GREEN,  actual B_YELLOW
```

```
Failure Category : COUNTER_ERROR
Severity         : HIGH
Expected         : A_YELLOW
Actual           : B_GREEN
```

Then: `COUNTER_ERROR → Neo4j → Groq AI → Root Cause → Recommendation`.
A real Groq response for this run:

> **Root cause:** GREEN_TICKS parameter is set to 2 instead of the
> required 4, causing the green states to end prematurely.
> **Recommendation:** change `localparam int GREEN_TICKS = 2;` to
> `localparam int GREEN_TICKS = 4;`. **Confidence:** 99%

### 14. ALU PASS demo

Select **4-bit ALU** + **Passing**.

```
Total Tests : 4
Passed      : 4
Failed      : 0
Status      : PASSED

✓ TEST_1 — ADD  — PASS    A=5 B=3 -> 8
✓ TEST_2 — SUB  — PASS    A=7 B=2 -> 5
✓ TEST_3 — AND  — PASS    A=6 B=3 -> 2
✓ TEST_4 — OR   — PASS    A=6 B=3 -> 7
```

### 15. ALU FAIL demo

Select **4-bit ALU** + **Failing**.

The bug is one line in `verilog/alu/failing/alu.sv`:

```systemverilog
OP_OR  : result = a & b;   // BUG: OR opcode wired to AND
```

```
Total Tests : 4
Passed      : 3
Failed      : 1
Status      : FAILED

✓ TEST_1 — ADD  — PASS
✓ TEST_2 — SUB  — PASS
✓ TEST_3 — AND  — PASS
✗ TEST_4 — OR   — FAIL    expected 7, actual 2
```

```
Failure Category : OUTPUT_MISMATCH
Severity         : MEDIUM
Expected         : 7
Actual           : 2
```

Then: `OUTPUT_MISMATCH → Neo4j → Groq AI → Root Cause → Recommendation`.
A real Groq response for this run:

> **Root cause:** OR opcode incorrectly performs AND operation.
> **Explanation:** the case for `OP_OR` assigns `result = a & b`, so the
> OR test produces 2 (6&3) instead of the expected 7 (6|3).
> **Recommendation:** replace `OP_OR : result = a & b;` with
> `OP_OR : result = a | b;`. **Confidence:** 100%

---

## 16. GraphQL examples

Open <http://localhost:8000/graphql> and paste these in.

### Create the project

```graphql
mutation {
  createProject(
    projectId: "P001"
    name: "Traffic Light and ALU Verification"
    description: "SystemVerilog RTL verification with Icarus Verilog, Neo4j and Groq"
  ) {
    projectId
    name
    createdAt
  }
}
```

### Run verification — traffic light, passing

```graphql
mutation {
  runVerification(
    projectId: "P001"
    example: "traffic_light"
    scenario: "passing"
  ) {
    jobId
    status
  }
}
```

### Run verification — ALU, failing

```graphql
mutation {
  runVerification(
    projectId: "P001"
    example: "alu"
    scenario: "failing"
  ) {
    jobId
    status
  }
}
```

### Poll the job

```graphql
query {
  verificationJob(jobId: "JOB-xxxxxxxxxxxx") {
    jobId
    status
    progress
    errorMessage
  }
}
```

### Full result, read back out of Neo4j

```graphql
query {
  verificationResult(jobId: "JOB-xxxxxxxxxxxx") {
    status
    simulation { totalTests passedTests failedTests status duration }
    tests      { testId name status expected actual }
    failures   { category severity expected actual message }
    aiAnalyses { rootCause explanation recommendation confidence }
    waveform   { fileName filePath }
    traceability { level label value }
  }
}
```

### Other queries

```graphql
query { projects { projectId name createdAt } }

query { project(projectId: "P001") { name description } }

query { failures(jobId: "JOB-xxxxxxxxxxxx") { category severity expected actual } }

query { aiAnalysis(jobId: "JOB-xxxxxxxxxxxx") { rootCause confidence } }

query { health { status neo4j groq iverilog } }
```

---

## 17. Neo4j queries

Paste these into the Neo4j Browser on your AuraDB instance.

### The whole graph for one job

```cypher
MATCH path = (p:Project)-[:HAS_JOB]->(j:VerificationJob {jobId: $jobId})
             -[:PRODUCED]->(s:Simulation)
OPTIONAL MATCH (s)-[:HAS_TEST]->(t:Test)
OPTIONAL MATCH (s)-[:HAS_FAILURE]->(f:Failure)-[:ANALYZED_BY]->(a:AIAnalysis)
RETURN path, t, f, a;
```

### Full traceability chain

```cypher
MATCH (p:Project)-[:HAS_JOB]->(j:VerificationJob {jobId: $jobId})
OPTIONAL MATCH (j)-[:USES_RTL]->(r:RTLModule)
OPTIONAL MATCH (j)-[:USES_TESTBENCH]->(tb:Testbench)
OPTIONAL MATCH (j)-[:PRODUCED]->(s:Simulation)
OPTIONAL MATCH (s)-[:HAS_FAILURE]->(f:Failure)
OPTIONAL MATCH (f)-[:ANALYZED_BY]->(a:AIAnalysis)
RETURN p.name        AS project,
       r.fileName    AS rtlModule,
       tb.fileName   AS testbench,
       j.jobId       AS job,
       s.status      AS simulation,
       f.category    AS failureCategory,
       f.severity    AS severity,
       a.rootCause   AS aiRootCause,
       a.confidence  AS confidence;
```

### Every test of the most recent job (PASS and FAIL)

```cypher
MATCH (j:VerificationJob)-[:PRODUCED]->(s:Simulation)-[:HAS_TEST]->(t:Test)
RETURN j.jobId, t.number, t.name, t.status, t.expected, t.actual
ORDER BY j.createdAt DESC, t.number
LIMIT 20;
```

### Failure categories across all runs

```cypher
MATCH (f:Failure)
RETURN f.category AS category, f.severity AS severity, count(*) AS occurrences
ORDER BY occurrences DESC;
```

### AI analyses with their failures

```cypher
MATCH (f:Failure)-[:ANALYZED_BY]->(a:AIAnalysis)
RETURN f.category, f.expected, f.actual, a.rootCause, a.confidence
ORDER BY a.createdAt DESC
LIMIT 10;
```

### Pass rate per RTL module

```cypher
MATCH (j:VerificationJob)-[:USES_RTL]->(r:RTLModule)
MATCH (j)-[:PRODUCED]->(s:Simulation)
RETURN r.moduleName            AS module,
       sum(s.passedTests)      AS passed,
       sum(s.failedTests)      AS failed,
       count(s)                AS runs;
```

### Waveforms on disk

```cypher
MATCH (s:Simulation)-[:GENERATED]->(w:Waveform)
RETURN w.fileName, w.filePath, s.status
ORDER BY s.simulationId DESC LIMIT 10;
```

### Reset the graph (optional, destructive)

```cypher
MATCH (n)
WHERE n:Project OR n:RTLModule OR n:Testbench OR n:VerificationJob
   OR n:Simulation OR n:Test OR n:Failure OR n:Waveform OR n:AIAnalysis
DETACH DELETE n;
```

---

## 18. Expected results

| Demo | Example | Scenario | Total | Passed | Failed | Status | Category | Severity |
|---|---|---|---|---|---|---|---|---|
| 1 | Traffic Light | passing | 4 | 4 | 0 | PASSED | — | — |
| 2 | Traffic Light | failing | 4 | 2 | 2 | FAILED | COUNTER_ERROR | HIGH |
| 3 | 4-bit ALU | passing | 4 | 4 | 0 | PASSED | — | — |
| 4 | 4-bit ALU | failing | 4 | 3 | 1 | FAILED | OUTPUT_MISMATCH | MEDIUM |

Job status sequence and progress:

```
QUEUED(0) -> COMPILING(20) -> SIMULATING(50) -> PARSING(70)
          -> ANALYZING(90, only if a test failed) -> COMPLETED(100)
```

These designs simulate in milliseconds, so the UI often jumps straight
from `COMPILING` to `PARSING` — the intermediate states are real, just
too fast to catch at a 1 second poll interval.

Artifacts per run, in `data/jobs/<jobId>/`:

```
simulation.vvp     compiled image
simulation.log     raw vvp output -- the source of truth for PASS/FAIL
waveform.vcd       open with: gtkwave data/jobs/<jobId>/waveform.vcd
```

---

## 19. Troubleshooting

**`iverilog: command not found`, or `/health` shows `iverilog: not found on PATH`**
Install Icarus Verilog (section 6) and reopen the terminal. If it lives
somewhere unusual, set `IVERILOG_BIN=/full/path/to/iverilog` in `.env`.

**`sorry: constructs of this type are not supported` / syntax errors on `logic`, `always_ff`**
Your Icarus Verilog is older than 11.0, or `-g2012` is missing. Check
`iverilog -V`, and upgrade if needed.

**`/health` shows `"neo4j": "disconnected"`**
Read `neo4j_error` in the same response. Common causes:
- wrong `NEO4J_PASSWORD` → `AuthError ... Unauthorized`
- wrong `NEO4J_USERNAME` or `NEO4J_DATABASE` — check the credentials
  file you downloaded from AuraDB; most instances use `neo4j` for both,
  but some use the instance id
- URI missing the `neo4j+s://` scheme → `ConfigurationError: URI scheme`
- the AuraDB free instance is **paused** — resume it in the console
- corporate firewall blocking outbound TLS on port 7687

**Streamlit says "Cannot reach the backend"**
The FastAPI process is not running. Start it in another terminal:
`uvicorn backend.main:app --reload --port 8000`. If you moved the backend
to another port, update `GRAPHQL_URL` in `.env`.

**AI section says `[AI unavailable]`**
`GROQ_API_KEY` is missing or invalid, or the Groq API returned an error.
Verification results are unaffected — only the narration is. Check the
backend log for the scrubbed Groq error.

**`Simulation produced no TEST_n lines to parse`**
The design compiled but the testbench printed nothing matching the log
contract. Inspect `data/jobs/<jobId>/simulation.log`.

**No `waveform.vcd`**
The testbench needs `$dumpfile("waveform.vcd")` and `$dumpvars(0, <tb>)`.
Both supplied testbenches have them.

**Job stuck in `QUEUED`**
All 4 worker threads are busy, or the backend was restarted mid-run
(job state lives in memory plus Neo4j; a restart loses in-flight jobs).
Restart the backend and re-run.

**`Neo4j error while ...` warning on an otherwise successful job**
The simulation and parsing succeeded but a graph write failed. The
verification result is still correct and shown; the graph is incomplete
for that job. Fix the connection and re-run.

**Port already in use**
```bash
uvicorn backend.main:app --reload --port 8001
streamlit run frontend/app.py --server.port 8502
```
Then set `GRAPHQL_URL=http://localhost:8001/graphql` in `.env`.

**Tests fail with `ModuleNotFoundError: backend`**
Run `pytest` from the `ai_rtl_debugger/` directory.

---

## Quick reference

```bash
cd ai_rtl_debugger
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then fill in your credentials
iverilog -V
pytest

# terminal 1
uvicorn backend.main:app --reload --port 8000
# terminal 2
streamlit run frontend/app.py
# browser
# http://localhost:8501
```
