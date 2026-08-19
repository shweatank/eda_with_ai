import subprocess
import shutil
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException

app = FastAPI(title="Logic Gate Simulator API")

BASE_DIR = Path(__file__).resolve().parent
VCD_FILE = BASE_DIR / "logic_gates.vcd"

VALID_GATES = {"and_gate", "or_gate", "nor_gate", "not_gate", "nand_gate"}


def check_gate(gate_name: str):
    if gate_name not in VALID_GATES:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown gate '{gate_name}'. Valid: {sorted(VALID_GATES)}",
        )


@app.get("/")
def root():
    return {
        "endpoints": [
            "/simulate",
            "/simulate/{gate_name}",
            "/waveform",
            "/waveform/{gate_name}",
            "/gtkwave",
            "/gtkwave/{gate_name}",
        ],
        "available_gates": sorted(VALID_GATES),
        "note": (
            "All gates now live in a single logic_gates.sv/.py testbench. "
            "POST /simulate runs every gate's test in one go. "
            "POST /simulate/{gate_name} runs just that gate's test via cocotb TESTCASE "
            "filtering. Both write to the same logic_gates.vcd (it includes all signals)."
        ),
    }


def _run_make(testcase: Optional[str] = None):
    # Clean stale build artifacts so cocotb always recompiles fresh
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
                   f"Check the $dumpfile name inside logic_gates.sv.",
        )

    return result


@app.post("/simulate")
def simulate_all():
    """Run every gate's test against the single logic_gates module."""
    result = _run_make()
    return {
        "message": "Simulation complete for all gates",
        "vcd_file": str(VCD_FILE),
        "stdout": result.stdout,
    }


@app.post("/simulate/{gate_name}")
def simulate(gate_name: str):
    """Run only the given gate's test, via cocotb TESTCASE filtering."""
    check_gate(gate_name)
    result = _run_make(testcase=f"test_{gate_name}")
    return {
        "message": f"Simulation complete for {gate_name}",
        "vcd_file": str(VCD_FILE),
        "stdout": result.stdout,
    }


@app.get("/waveform")
def waveform():
    if VCD_FILE.exists():
        return {"status": "ready", "message": "Waveform file exists.", "vcd_file": str(VCD_FILE)}
    return {
        "status": "not_found",
        "message": "No waveform found. Call POST /simulate (or /simulate/{gate_name}) first.",
    }


@app.get("/waveform/{gate_name}")
def waveform_gate(gate_name: str):
    # gate_name is only used to validate the request; all gates share one vcd file
    check_gate(gate_name)
    return waveform()


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
    return {"message": "GTKWave launched for logic_gates.vcd"}


@app.post("/gtkwave/{gate_name}")
def open_gtkwave_gate(gate_name: str):
    check_gate(gate_name)
    return open_gtkwave()
