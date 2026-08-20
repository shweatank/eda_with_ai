"""
main.py

Local web GUI (FastAPI) for running the logic gates cocotb test suite.

Runs each gate's test via `make` (same as the command line), captures
the output, and parses out:
  - PASS/FAIL lines
  - The Gemini analysis block printed by test_gates.py

Setup:
    pip install fastapi uvicorn

Run:
    Place this file (and the static/ folder) INSIDE your logic_gates
    project directory, alongside your Makefile, gates.v, test_gates.py,
    gate_analysis.py, llm_client.py, and .env.

    Then:
        uvicorn main:app --reload

    Open http://127.0.0.1:8000 in your browser.
"""

import os
import re
import subprocess

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="Logic Gates GUI")

# Directory this script lives in -- assumed to be the project root
# (where the Makefile, gates.v, etc. live).
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

GATES = [
    {"toplevel": "and_gate", "testcase": "test_and", "label": "AND"},
    {"toplevel": "or_gate", "testcase": "test_or", "label": "OR"},
    {"toplevel": "not_gate", "testcase": "test_not", "label": "NOT"},
    {"toplevel": "xor_gate", "testcase": "test_xor", "label": "XOR"},
    {"toplevel": "nand_gate", "testcase": "test_nand", "label": "NAND"},
    {"toplevel": "nor_gate", "testcase": "test_nor", "label": "NOR"},
    {"toplevel": "xnor_gate", "testcase": "test_xnor", "label": "XNOR"},
]
VALID_COMBOS = {g["toplevel"]: g["testcase"] for g in GATES}


class GateResult(BaseModel):
    success: bool
    pass_lines: list[str]
    analysis: str | None
    raw_output: str


def run_gate_test(toplevel: str, testcase: str) -> GateResult:
    """Clean-rebuild and run one gate's cocotb test, then parse the output."""
    # Clean previous build (required -- stale sim_build causes wrong-toplevel errors)
    subprocess.run(
        ["rm", "-rf", "sim_build", "results.xml"],
        cwd=PROJECT_DIR,
        capture_output=True,
    )

    result = subprocess.run(
        ["make", f"TOPLEVEL={toplevel}", f"COCOTB_TESTCASE={testcase}"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )

    output = result.stdout + "\n" + result.stderr

    pass_lines = re.findall(r"^PASS:.*$", output, re.MULTILINE)

    analysis_match = re.search(
        r"--- Gemini analysis: .*? ---\n(.*?)\n---------------------------------",
        output,
        re.DOTALL,
    )
    analysis = analysis_match.group(1).strip() if analysis_match else None

    # Defensive: force analysis to be a plain string or None no matter what
    # the regex/match produced -- prevents a Pydantic validation crash from
    # ever taking down the whole endpoint.
    if analysis is not None and not isinstance(analysis, str):
        analysis = str(analysis)

    test_passed = "TESTS=" in output and "FAIL=0" in output

    return GateResult(
        success=bool(result.returncode == 0 and test_passed),
        pass_lines=[str(line) for line in pass_lines],
        analysis=analysis,
        raw_output=output,
    )


@app.get("/api/gates")
def list_gates():
    return GATES


@app.get("/api/run/{toplevel}/{testcase}", response_model=GateResult)
def run_single(toplevel: str, testcase: str):
    if VALID_COMBOS.get(toplevel) != testcase:
        raise HTTPException(status_code=400, detail="Unknown gate/testcase combination")

    try:
        return run_gate_test(toplevel, testcase)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Test timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")


# Serve the frontend
app.mount("/static", StaticFiles(directory=os.path.join(PROJECT_DIR, "static")), name="static")


@app.get("/")
def index():
    return FileResponse(os.path.join(PROJECT_DIR, "static", "index.html"))