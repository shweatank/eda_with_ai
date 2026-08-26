import subprocess
import shutil
import os
import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from openai import OpenAI

app = FastAPI(title="Parameterized RAM Verification & Synthesis API")

BASE_DIR = Path(__file__).resolve().parent
VCD_FILE = BASE_DIR / "para_ram.vcd"
SV_FILE = BASE_DIR / "para_ram.sv"
NETLIST_FILE = BASE_DIR / "para_ram_netlist.v"
TOP_MODULE = "para_ram"

# --------------------------------------------------
# Gemini (OpenAI-compatible) client
# --------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = None
if GEMINI_API_KEY:
    client = OpenAI(
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")  # verify this string in Google's docs


@app.get("/")
def root():
    return {
        "endpoints": [
            "/simulate",
            "/waveform",
            "/gtkwave",
            "/synthesize",
            "/show",
            "/ai-report",
        ],
        "top_module": TOP_MODULE,
        "note": (
            "Parameterized RAM lives in para_ram.sv / test_para_ram.py. "
            "POST /simulate runs cocotb (optionally with addr_width/data_width params). "
            "POST /synthesize runs Yosys and produces para_ram_netlist.v. "
            "POST /ai-report runs both and sends the combined results to Gemini "
            "for a human-readable verification report."
        ),
    }


# --------------------------------------------------
# Simulation (cocotb via make)
# --------------------------------------------------
def _run_make(addr_width: Optional[int] = None, data_width: Optional[int] = None):
    shutil.rmtree(BASE_DIR / "sim_build", ignore_errors=True)
    (BASE_DIR / "results.xml").unlink(missing_ok=True)

    cmd = ["make"]
    if addr_width is not None:
        cmd.append(f"PARAM_ADDR_WIDTH={addr_width}")
    if data_width is not None:
        cmd.append(f"PARAM_DATA_WIDTH={data_width}")

    try:
        result = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Simulation timed out")

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail={"message": "Simulation failed", "stdout": result.stdout, "stderr": result.stderr},
        )

    if not VCD_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail=f"make succeeded but {VCD_FILE.name} was not created. "
                   f"Check the $dumpfile name inside para_ram.sv.",
        )

    return result


@app.post("/simulate")
def simulate(addr_width: Optional[int] = None, data_width: Optional[int] = None):
    """
    Run the parameterized RAM cocotb testbench.
    Optionally override size via query params, e.g.:
    POST /simulate?addr_width=12&data_width=8
    """
    if addr_width is not None and addr_width > 20:
        raise HTTPException(
            status_code=400,
            detail="addr_width too large for simulation (max 20, i.e. 1MB). "
                   "Behavioral memory arrays don't scale to real hardware sizes like 16GB/64GB.",
        )

    result = _run_make(addr_width=addr_width, data_width=data_width)
    return {
        "message": "Simulation complete for para_ram",
        "addr_width": addr_width if addr_width is not None else 8,
        "data_width": data_width if data_width is not None else 8,
        "vcd_file": str(VCD_FILE),
        "stdout": result.stdout,
    }


@app.get("/waveform")
def waveform():
    if VCD_FILE.exists():
        return {"status": "ready", "message": "Waveform file exists.", "vcd_file": str(VCD_FILE)}
    return {
        "status": "not_found",
        "message": "No waveform found. Call POST /simulate first.",
    }


@app.post("/gtkwave")
def open_gtkwave():
    if not VCD_FILE.exists():
        raise HTTPException(status_code=404, detail=f"{VCD_FILE.name} not found. Call /simulate first.")
    try:
        subprocess.Popen(
            ["gtkwave", str(VCD_FILE)],
            cwd=BASE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="gtkwave command not found. Is it installed and on PATH?")
    return {"message": "GTKWave launched for para_ram.vcd"}


# --------------------------------------------------
# Synthesis (Yosys)
# --------------------------------------------------
def _run_yosys():
    if not SV_FILE.exists():
        raise HTTPException(status_code=404, detail=f"{SV_FILE.name} not found in {BASE_DIR}")

    yosys_script = (
        f"read_verilog -DSYNTHESIS {SV_FILE.name}; "
        f"synth -top {TOP_MODULE}; "
        f"write_verilog -noattr {NETLIST_FILE.name}"
    )

    try:
        result = subprocess.run(
            ["yosys", "-p", yosys_script],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="yosys command not found. Is it installed and on PATH?")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Synthesis timed out")

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail={"message": "Synthesis failed", "stdout": result.stdout, "stderr": result.stderr},
        )

    if not NETLIST_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail=f"yosys ran but {NETLIST_FILE.name} was not created.",
        )

    return result


@app.post("/synthesize")
def synthesize():
    """Run read_verilog -> synth -top para_ram -> write_verilog via Yosys (uses default param values)."""
    result = _run_yosys()
    latch_detected = "latch" in result.stdout.lower()
    return {
        "message": "Synthesis complete for para_ram",
        "netlist_file": str(NETLIST_FILE),
        "latch_warning": latch_detected,
        "stdout": result.stdout,
    }


@app.post("/show")
def show_schematic():
    """Launch the Yosys 'show' graphviz viewer (non-blocking, needs an X server)."""
    if not NETLIST_FILE.exists():
        raise HTTPException(status_code=404, detail="Run /synthesize first.")
    yosys_script = (
        f"read_verilog -noattr {NETLIST_FILE.name}; show -format dot -prefix para_ram_show"
    )
    try:
        subprocess.Popen(
            ["yosys", "-p", yosys_script],
            cwd=BASE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="yosys command not found. Is it installed and on PATH?")
    return {"message": "Yosys show launched (requires a working X server / xdot)."}


# --------------------------------------------------
# AI Report (Gemini, OpenAI-compatible endpoint)
# --------------------------------------------------
@app.post("/ai-report")
def ai_report(addr_width: Optional[int] = None, data_width: Optional[int] = None):
    if client is None:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not set in the environment. Set it before starting the server.",
        )

    if addr_width is not None and addr_width > 20:
        raise HTTPException(
            status_code=400,
            detail="addr_width too large for simulation (max 20, i.e. 1MB).",
        )

    sim_result = _run_make(addr_width=addr_width, data_width=data_width)
    synth_result = _run_yosys()
    latch_detected = "latch" in synth_result.stdout.lower()

    results = {
        "module": TOP_MODULE,
        "rtl_file": f"rtl/{SV_FILE.name}",
        "parameters": {
            "addr_width": addr_width if addr_width is not None else 8,
            "data_width": data_width if data_width is not None else 8,
        },
        "simulation": {
            "status": "success" if sim_result.returncode == 0 else "failed",
            "return_code": sim_result.returncode,
            "stdout": sim_result.stdout,
            "stderr": sim_result.stderr,
        },
        "synthesis": {
            "status": "success" if synth_result.returncode == 0 else "failed",
            "return_code": synth_result.returncode,
            "latch_detected": latch_detected,
            "netlist_generated": NETLIST_FILE.exists(),
            "stdout": synth_result.stdout,
            "stderr": synth_result.stderr,
        },
    }

    prompt = f"""
You are an EDA verification and synthesis analysis assistant.
Analyze the following RTL verification and synthesis results.
Generate a clean, professional, human-readable
EDA AI Verification Report suitable for displaying
in a terminal.
IMPORTANT:
- Do NOT return JSON.
- Do NOT use Markdown headings.
- Do NOT use ``` code blocks.
- Use plain text only.
- Do not invent information.
- Clearly distinguish warnings from failures.
- Base your analysis ONLY on the provided results.

REPORT FORMAT:
==================================================
EDA AI VERIFICATION REPORT
==================================================
RTL MODULE
----------
Module   : {TOP_MODULE}
RTL File : rtl/{SV_FILE.name}

SIMULATION
----------
Simulator : <simulator>
Tests     : <number>
Passed    : <number>
Failed    : <number>
Skipped   : <number>
Status    : <PASS/FAIL>

SYNTHESIS
---------
Tool       : Yosys
Top Module : {TOP_MODULE}
Parsing    : <SUCCESS/FAILED>
Latch      : <NONE DETECTED / DETECTED>
Netlist    : <GENERATED / NOT GENERATED>

WARNINGS
--------
<List warnings>

AI ANALYSIS
-----------
<2-4 concise observations>

Recommendation:
<practical recommendation>

FINAL STATUS
------------
<PASS/FAIL>
==================================================

EDA TOOL RESULTS:
{json.dumps(results, indent=2)}
"""

    try:
        response = client.chat.completions.create(
            model=GEMINI_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI report generation failed: {e}")

    ai_analysis = response.choices[0].message.content
    print("\n" + ai_analysis)

    overall_pass = sim_result.returncode == 0 and synth_result.returncode == 0 and not latch_detected

    return {
        "status": "PASS" if overall_pass else "FAIL",
        "ai_analysis": ai_analysis,
    }
