import subprocess
import shutil
import os
import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from openai import OpenAI

app = FastAPI(title="ROM Verification & Synthesis API")

BASE_DIR = Path(__file__).resolve().parent
VCD_FILE = BASE_DIR / "rom.vcd"
SV_FILE = BASE_DIR / "rom.sv"
NETLIST_FILE = BASE_DIR / "rom_netlist.v"
TOP_MODULE = "rom"

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
            "ROM lives in rom.sv / test_rom.py. POST /simulate runs cocotb. "
            "POST /synthesize runs Yosys and produces rom_netlist.v. "
            "POST /ai-report runs both and sends the combined results to Gemini "
            "for a human-readable verification report."
        ),
    }


# --------------------------------------------------
# Simulation (cocotb via make)
# --------------------------------------------------
def _run_make(testcase: Optional[str] = None):
    shutil.rmtree(BASE_DIR / "sim_build", ignore_errors=True)
    (BASE_DIR / "results.xml").unlink(missing_ok=True)

    cmd = ["make"]
    if testcase:
        cmd.append(f"TESTCASE={testcase}")

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
                   f"Check the $dumpfile name inside rom.sv.",
        )

    return result


@app.post("/simulate")
def simulate():
    """Run the ROM cocotb testbench."""
    result = _run_make()
    return {
        "message": "Simulation complete for rom",
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
    return {"message": "GTKWave launched for rom.vcd"}


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
    """Run read_verilog -> synth -top rom -> write_verilog via Yosys."""
    result = _run_yosys()
    latch_detected = "latch" in result.stdout.lower()
    return {
        "message": "Synthesis complete for rom",
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
        f"read_verilog -noattr {NETLIST_FILE.name}; show -format dot -prefix rom_show"
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
def ai_report():
    if client is None:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not set in the environment. Set it before starting the server.",
        )

    sim_result = _run_make()
    synth_result = _run_yosys()
    latch_detected = "latch" in synth_result.stdout.lower()

    results = {
        "module": TOP_MODULE,
        "rtl_file": f"rtl/{SV_FILE.name}",
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
