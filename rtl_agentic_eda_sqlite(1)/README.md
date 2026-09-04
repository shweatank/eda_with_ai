# RTL Agentic EDA — FastAPI-only GUI

Local agentic RTL -> simulation -> synthesis -> STA -> physical verification using Ollama.
**Node.js/npm are not required.**

## Models
- Gemma 4 26B: planning
- Qwen2.5-Coder 7B: SystemVerilog + Cocotb generation/repair
- Llama 3.1: failure diagnosis + final review

## Local setup (macOS/Linux)

### 1. Verify Python
```bash
python3 --version
```
Python 3.11+ is recommended.

### 2. Verify Ollama and models
```bash
ollama --version
ollama list
```
Expected model names:
```text
qwen2.5-coder:7b
llama3.1:latest
gemma4:26b
```
If Ollama is not running, start the Ollama application or:
```bash
ollama serve
```
Optional model smoke tests:
```bash
ollama run qwen2.5-coder:7b
ollama run llama3.1:latest
ollama run gemma4:26b
```

### 3. Create virtual environment
From the project root:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure
```bash
cp .env.example .env
```
Default values use your three local models and `MOCK_EDA=true`.

### 5. Start FastAPI
```bash
source .venv/bin/activate
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
Open:
- GUI: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

There is no frontend server. FastAPI serves HTML/CSS/JavaScript directly.

## First test
Keep `MOCK_EDA=true`. In the GUI enter:
```text
Create a 4 bit adder and run the complete EDA flow.
```
Click **Run Pipeline**.

The live dashboard shows:
1. Planning
2. RTL generation
3. Cocotb generation
4. Simulation
5. Synthesis
6. OpenSTA
7. Physical design
8. Physical verification

## Agentic failure verification
Each executable stage returns success/failure, return code, output and metrics. On failure:
```text
EDA stage fails
   -> capture stdout/stderr
   -> Llama diagnoses root cause
   -> diagnosis + repair instructions are shown live
   -> retry up to MAX_RETRIES
   -> pass continues pipeline / final failure stops pipeline
```
Generation stages can use Qwen repair; tool stages currently record diagnosis and retry safely.
The architecture intentionally does NOT give an LLM unrestricted shell access.

## Generated files
Each job is under:
```text
runs/<job_id>/
  plan.json
  rtl/design.sv
  testbench/test_design.py
  synthesis.ys
  sta.tcl
  reports/report.json
  reports/report.html
```
The GUI has tabs for RTL, Cocotb and the final report.

## Real EDA mode
After the mock flow works, install the actual tools and set:
```text
MOCK_EDA=false
```

### Simulation
Install/configure Icarus Verilog or Verilator and Cocotb. Verify, for example:
```bash
iverilog -V
python -c "import cocotb; print(cocotb.__version__)"
```
The starter simulator adapter invokes `pytest -q -s` in the generated testbench directory;
for a production flow, replace it with your preferred Cocotb runner/Makefile configuration.

### Yosys
Verify:
```bash
yosys -V
```
The generated `synthesis.ys` reads the generated SystemVerilog and writes a synthesized netlist.

### OpenSTA
Verify:
```bash
sta -version
```
A real STA run requires technology-specific Liberty and SDC files. Edit/configure `sta.tcl`
for your target PDK. Do not treat mock timing numbers as real timing results.

### OpenROAD/OpenLane
Configure the adapter for your installed version and selected PDK. Physical design is
technology-specific: floorplan, placement, CTS, routing, extraction, DRC and LVS all need
appropriate PDK configuration. The starter adapter is a safe integration boundary, not a
universal PDK configuration.

## Recommended progression
```text
1. Ollama + models
2. MOCK_EDA=true
3. FastAPI GUI + WebSocket
4. Real Cocotb simulation
5. Real Yosys
6. Real OpenSTA + Liberty/SDC
7. OpenROAD/OpenLane
8. DRC/LVS
9. stronger artifact-aware agent repairs
10. regression suite
```

## Troubleshooting

### `npm: command not found`
Ignore it. This version does not use Node.js/npm.

### Ollama connection refused
```bash
ollama list
curl http://localhost:11434/api/tags
```
Start Ollama if necessary.

### Model not found
Make sure `.env` exactly matches `ollama list`.

### FastAPI import error
Run from the project root with the venv activated:
```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

### GUI shows WS ERROR
Check the FastAPI terminal for exceptions and make sure port 8000 is reachable.

### Real EDA command not found
```bash
which yosys
which sta
which iverilog
```
Ensure the tools are on PATH.

## SQLite persistence

Pipeline state is persisted automatically in `eda_pipeline.db` at the project root. The database stores:

- jobs and prompts
- current pipeline status
- every pipeline step, attempt, start/end time, output, metrics and errors
- generated artifact paths
- agent failure diagnosis / repair history
- live pipeline events
- final report JSON

The DB uses SQLite WAL mode, so reads can happen while the pipeline is writing.

Useful endpoints:

```bash
# Health
curl http://127.0.0.1:8000/health

# List saved jobs
curl http://127.0.0.1:8000/api/designs

# Read a saved job after restarting FastAPI
curl http://127.0.0.1:8000/api/design/<JOB_ID>
```

You do not need to install a separate database server. SQLite is included with Python.
