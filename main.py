"""
main.py

Local web GUI (FastAPI) for running the logic gates cocotb test suite.

Runs each gate's test via `make` (same as the command line), captures
the output, and provides streaming LLM analysis endpoints.

Setup:
    pip install fastapi uvicorn openai python-dotenv

Run:
    Place this file (and the static/ folder) INSIDE your logic_gates
    project directory, alongside your Makefile, all_designs.v, test_all_designs.py,
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
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from llm_client import ask_llm_stream

app = FastAPI(title="Logic Gates GUI")

# Directory this script lives in -- assumed to be the project root
# (where the Makefile, all_designs.v, etc. live).
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

GATES = [
    {"toplevel": "and_gate", "testcase": "test_and", "label": "AND"},
    {"toplevel": "or_gate", "testcase": "test_or", "label": "OR"},
    {"toplevel": "not_gate", "testcase": "test_not", "label": "NOT"},
    {"toplevel": "xor_gate", "testcase": "test_xor", "label": "XOR"},
    {"toplevel": "nand_gate", "testcase": "test_nand", "label": "NAND"},
    {"toplevel": "nor_gate", "testcase": "test_nor", "label": "NOR"},
    {"toplevel": "xnor_gate", "testcase": "test_xnor", "label": "XNOR"},
    {"toplevel": "logic_model", "testcase": "test_logic_exhaustive", "label": "LOGIC MODEL"},
    {"toplevel": "adder", "testcase": "test_add_edge", "label": "ADDER"},
    {"toplevel": "subtractor", "testcase": "test_sub_edge", "label": "SUBTRACTOR"},
    {"toplevel": "multiplier", "testcase": "test_mul_edge", "label": "MULTIPLIER"},
    {"toplevel": "divider", "testcase": "test_div_edge", "label": "DIVIDER"},
    {"toplevel": "alu", "testcase": "test_alu_random", "label": "ALU"},
]
VALID_COMBOS = {g["toplevel"]: g["testcase"] for g in GATES}


class GateResult(BaseModel):
    success: bool
    pass_lines: list[str]
    analysis: str | None
    raw_output: str


class StreamAnalysisRequest(BaseModel):
    toplevel: str
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


@app.post("/api/analyze-stream")
async def analyze_simulation_stream(req: StreamAnalysisRequest):
    """Stream live Gemini analysis of simulation output back to the frontend."""
    prompt = f"""
    Analyze the following cocotb simulation results for the Verilog module '{req.toplevel}':

    Simulation Output:
    {req.raw_output}

    Provide a concise explanation of whether the design passed, any failures detected, and truth table behavior.
    """
    try:
        generator = ask_llm_stream(
            prompt=prompt,
            system_prompt="You are an expert Verilog and digital design EDA assistant.",
        )
        return StreamingResponse(generator, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Stream Error: {e}")


# Serve the frontend
app.mount("/static", StaticFiles(directory=os.path.join(PROJECT_DIR, "static")), name="static")


@app.get("/")
def index():
    return FileResponse(os.path.join(PROJECT_DIR, "static", "index.html"))