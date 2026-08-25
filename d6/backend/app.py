from flask import Flask, jsonify, render_template
import os
import subprocess
import requests

# =========================================================
# PATH CONFIGURATION
# =========================================================

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BACKEND_DIR, ".."))
TEMPLATE_DIR = os.path.join(PROJECT_DIR, "templates")

# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__, template_folder=TEMPLATE_DIR)

# =========================================================
# PROJECT FILES
# =========================================================

DESIGN_PATH   = os.path.join(PROJECT_DIR, "ram.sv")
TESTBENCH_PATH = os.path.join(PROJECT_DIR, "testbench_simpleram.py")
MAKEFILE_PATH = os.path.join(PROJECT_DIR, "Makefile")
NETLIST_PATH  = os.path.join(PROJECT_DIR, "simple_ram_netlist.v")
VCD_PATH      = os.path.join(PROJECT_DIR, "simple_ram.vcd")
PNG_PATH      = os.path.join(PROJECT_DIR, "simple_ram.png")

# =========================================================
# OLLAMA CONFIGURATION
# =========================================================

OLLAMA_URL   = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3.2"

# =========================================================
# HELPER FUNCTION
# =========================================================

def read_file(file_path):
    with open(file_path, "r", errors="ignore") as file:
        return file.read()

def ask_ollama(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=180
        )
        response.raise_for_status()
        data = response.json()
        ai_response = data.get("response", "No response received from Ollama.")
        response_upper = ai_response.upper()
        if "STATUS: FAIL" in response_upper:
            status = "FAIL"
        elif "STATUS: PASS" in response_upper:
            status = "PASS"
        else:
            status = "WARNING"
        return {"status": status, "details": ai_response}
    except Exception as error:
        return {"status": "ERROR", "details": str(error)}

# =========================================================
# REVIEWS
# =========================================================

def review_systemverilog():
    try:
        design_code = read_file(DESIGN_PATH)
        prompt = f"""
You are an expert RTL verification engineer.
Review this RAM design for syntax, correctness, and synthesizability.
Expected behavior: synchronous write/read with 8-bit address and data.

Return EXACTLY:
STATUS: PASS
ISSUES: - None
SUGGESTIONS: - Optional

OR
STATUS: FAIL
ISSUES: - Problem
SUGGESTIONS: - Fix

CODE:
{design_code}
"""
        return {"file": "ram.sv", "stage": "SystemVerilog Review", **ask_ollama(prompt)}
    except Exception as error:
        return {"stage": "SystemVerilog Review", "status": "ERROR", "details": str(error)}

def review_testbench():
    try:
        tb_code = read_file(TESTBENCH_PATH)
        prompt = f"""
You are an expert Cocotb engineer.
Review this testbench for syntax, coverage, and correctness.

Expected: write/read operations on RAM.

Return EXACTLY:
STATUS: PASS
ISSUES: - None
SUGGESTIONS: - Optional

OR
STATUS: FAIL
ISSUES: - Problem
SUGGESTIONS: - Fix

CODE:
{tb_code}
"""
        return {"file": "testbench_simpleram.py", "stage": "Testbench Review", **ask_ollama(prompt)}
    except Exception as error:
        return {"stage": "Testbench Review", "status": "ERROR", "details": str(error)}

def review_makefile():
    try:
        mk_code = read_file(MAKEFILE_PATH)
        prompt = f"""
You are an expert in GNU Make, Cocotb, Icarus Verilog, and Yosys.
Review this Makefile for correctness of targets (sim, netlist, png).

Return EXACTLY:
STATUS: PASS
ISSUES: - None
SUGGESTIONS: - Optional

OR
STATUS: FAIL
ISSUES: - Problem
SUGGESTIONS: - Fix

MAKEFILE:
{mk_code}
"""
        return {"file": "Makefile", "stage": "Makefile Review", **ask_ollama(prompt)}
    except Exception as error:
        return {"stage": "Makefile Review", "status": "ERROR", "details": str(error)}

def review_netlist():
    try:
        if not os.path.exists(NETLIST_PATH):
            return {"file": "simple_ram_netlist.v", "stage": "Netlist Review", "status": "FAIL", "details": "Netlist not found."}
        netlist_code = read_file(NETLIST_PATH)
        prompt = f"""
You are an expert synthesis engineer.
Review this netlist for syntax and correctness.

Return EXACTLY:
STATUS: PASS
ISSUES: - None
SUGGESTIONS: - Optional

OR
STATUS: FAIL
ISSUES: - Problem
SUGGESTIONS: - Fix

NETLIST:
{netlist_code}
"""
        return {"file": "simple_ram_netlist.v", "stage": "Netlist Review", **ask_ollama(prompt)}
    except Exception as error:
        return {"stage": "Netlist Review", "status": "ERROR", "details": str(error)}

# =========================================================
# EXECUTION
# =========================================================

def run_simulation():
    try:
        result = subprocess.run(["make"], cwd=PROJECT_DIR, capture_output=True, text=True, timeout=180)
        output = result.stdout + "\n" + result.stderr
        if result.returncode == 0:
            return {"stage": "Simulation", "status": "PASS", "details": "Simulation completed.", "output": output}
        return {"stage": "Simulation", "status": "FAIL", "details": "Simulation failed.", "output": output}
    except Exception as error:
        return {"stage": "Simulation", "status": "ERROR", "details": str(error)}

def generate_netlist():
    try:
        result = subprocess.run(["make", "netlist"], cwd=PROJECT_DIR, capture_output=True, text=True, timeout=180)
        output = result.stdout + "\n" + result.stderr
        if result.returncode == 0 and os.path.exists(NETLIST_PATH):
            return {"stage": "Netlist Generation", "status": "PASS", "details": "Netlist generated.", "output": output}
        return {"stage": "Netlist Generation", "status": "FAIL", "details": "Netlist generation failed.", "output": output}
    except Exception as error:
        return {"stage": "Netlist Generation", "status": "ERROR", "details": str(error)}

def generate_png():
    try:
        result = subprocess.run(["make", "png"], cwd=PROJECT_DIR, capture_output=True, text=True, timeout=180)
        output = result.stdout + "\n" + result.stderr
        if result.returncode == 0 and os.path.exists(PNG_PATH):
            return {"stage": "PNG Generation", "status": "PASS", "details": "PNG generated.", "output": output}
        return {"stage": "PNG Generation", "status": "FAIL", "details": "PNG generation failed.", "output": output}
    except Exception as error:
        return {"stage": "PNG Generation", "status": "ERROR", "details": str(error)}

def validate_vcd():
    try:
        if not os.path.exists(VCD_PATH):
            return {"file": "simple_ram.vcd", "stage": "VCD Validation", "status": "FAIL", "details": "VCD not found."}
        size = os.path.getsize(VCD_PATH)
        if size == 0:
            return {"file": "simple_ram.vcd", "stage": "VCD Validation", "status": "FAIL", "details": "VCD empty."}
        return {"file": "simple_ram.vcd", "stage": "VCD Validation", "status": "PASS", "details": f"VCD OK, size {size} bytes."}
    except Exception as error:
        return {"stage": "VCD Validation", "status": "ERROR", "details": str(error)}

def validate_png():
    try:
        if not os.path.exists(PNG_PATH):
            return {"file": "simple_ram.png", "stage": "PNG Validation", "status": "FAIL", "details": "PNG not found."}
        size = os.path.getsize(PNG_PATH)
        if size == 0:
            return {"file": "simple_ram.png", "stage": "PNG Validation", "status": "FAIL", "details": "PNG empty."}
        return {"file": "simple_ram.png", "stage": "PNG Validation", "status": "PASS", "details": f"PNG OK, size {size} bytes."}
    except Exception as error:
        return {"stage": "PNG Validation", "status": "ERROR", "details": str(error)}

# =========================================================
# ROUTES
# =========================================================

@app.route("/")
def index():
    return render_template("index.html")

