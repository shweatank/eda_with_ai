import os
import subprocess
import tempfile
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Verilog & Cocotb Simulation Engine API",
    description="Backend API to run Icarus Verilog + Cocotb simulations and return results.",
    version="1.0.0"
)

# Enable CORS so web applications (React, Vue, plain HTML) can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Default path to static project
SIM_DIR = os.path.expanduser("~/or_gate")

# Data model for dynamic code execution
class CustomSimulationRequest(BaseModel):
    verilog_code: str
    test_code: str


# -------------------------------------------------------------------
# 1. GET / -> API Health Check
# -------------------------------------------------------------------
@app.get("/")
def api_status():
    return {
        "status": "online",
        "engine": "Icarus Verilog + Cocotb",
        "default_dir": SIM_DIR
    }


# -------------------------------------------------------------------
# 2. GET & POST /run-sim -> Run static local ~/or_gate project
# -------------------------------------------------------------------
@app.get("/run-sim")
@app.post("/run-sim")
def run_default_simulation():
    """Executes 'make' inside the ~/or_gate directory."""
    if not os.path.exists(SIM_DIR):
        raise HTTPException(status_code=404, detail=f"Directory '{SIM_DIR}' not found")

    result = subprocess.run(
        ["make"],
        cwd=SIM_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr
    }


# -------------------------------------------------------------------
# 3. POST /simulate -> Execute dynamic user-provided code
# -------------------------------------------------------------------
@app.post("/simulate")
def run_custom_simulation(payload: CustomSimulationRequest):
    """Accepts custom Verilog and Python test code, runs it in a temp folder, and returns results."""
    with tempfile.TemporaryDirectory() as tmpdir:
        verilog_file = os.path.join(tmpdir, "design.sv")
        test_file = os.path.join(tmpdir, "test_design.py")
        makefile_path = os.path.join(tmpdir, "Makefile")

        # Write code to temp files
        with open(verilog_file, "w") as f:
            f.write(payload.verilog_code)

        with open(test_file, "w") as f:
            f.write(payload.test_code)

        # Create Makefile
        makefile_content = f"""SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += {verilog_file}
COCOTB_TOPLEVEL = or_gate
COCOTB_TEST_MODULES = test_design
WAVES = 1

include $(shell cocotb-config --makefiles)/Makefile.sim
"""
        with open(makefile_path, "w") as f:
            f.write(makefile_content)

        # Execute simulation
        try:
            result = subprocess.run(
                ["make"],
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=408, detail="Simulation execution timed out (10s limit).")

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }


# -------------------------------------------------------------------
# 4. GET /vcd -> Retrieve raw VCD waveform data
# -------------------------------------------------------------------
@app.get("/vcd")
def get_vcd_waveform():
    """Reads the generated dump_or.vcd file from ~/or_gate."""
    vcd_path = os.path.join(SIM_DIR, "dump_or.vcd")
    if not os.path.exists(vcd_path):
        vcd_path = os.path.join(SIM_DIR, "dump.vcd")
        
    if not os.path.exists(vcd_path):
        raise HTTPException(status_code=404, detail="Waveform file not found. Run /run-sim first.")

    with open(vcd_path, "r") as f:
        vcd_content = f.read()

    return {
        "file_found": True,
        "content": vcd_content
    }