import subprocess
import shutil
from pathlib import Path
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Logic Gate Simulator API")

BASE_DIR = Path(__file__).resolve().parent

VALID_GATES = {"and_gate", "or_gate", "nor_gate", "not_gate", "nand_gate"}


def vcd_path(gate_name: str) -> Path:
    return BASE_DIR / f"{gate_name}.vcd"


def check_gate(gate_name: str):
    if gate_name not in VALID_GATES:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown gate '{gate_name}'. Valid: {sorted(VALID_GATES)}",
        )


@app.get("/")
def root():
    return {
        "endpoints": ["/simulate/{gate_name}", "/waveform/{gate_name}", "/gtkwave/{gate_name}"],
        "available_gates": sorted(VALID_GATES),
    }


@app.post("/simulate/{gate_name}")
def simulate(gate_name: str):
    check_gate(gate_name)
    
    # Clean stale build artifacts so cocotb always recompiles fresh
    shutil.rmtree(BASE_DIR / "sim_build", ignore_errors=True)
    (BASE_DIR / "results.xml").unlink(missing_ok=True)

    try:
        result = subprocess.run(
            ["make", f"GATE={gate_name}"],
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

    vcd_file = vcd_path(gate_name)
    if not vcd_file.exists():
        raise HTTPException(
            status_code=500,
            detail=f"make succeeded but {vcd_file.name} was not created. "
                   f"Check the $dumpfile name inside {gate_name}.sv.",
        )

    return {
        "message": f"Simulation complete for {gate_name}",
        "vcd_file": str(vcd_file),
        "stdout": result.stdout,
    }


@app.get("/waveform/{gate_name}")
def waveform(gate_name: str):
    check_gate(gate_name)

    vcd_file = vcd_path(gate_name)
    if vcd_file.exists():
        return {"status": "ready", "message": "Waveform file exists.", "vcd_file": str(vcd_file)}
    else:
        return {
            "status": "not_found",
            "message": f"No waveform found for {gate_name}. Call POST /simulate/{gate_name} first.",
        }


@app.post("/gtkwave/{gate_name}")
def open_gtkwave(gate_name: str):
    check_gate(gate_name)

    vcd_file = vcd_path(gate_name)
    if not vcd_file.exists():
        raise HTTPException(status_code=404, detail=f"{vcd_file.name} not found. Call /simulate/{gate_name} first.")

    try:
        subprocess.Popen(
            ["gtkwave", str(vcd_file)],
            cwd=BASE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="gtkwave command not found. Is it installed and on PATH?")

    return {"message": f"GTKWave launched for {gate_name}.vcd"}
