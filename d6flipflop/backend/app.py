from flask import Flask, jsonify, render_template
import os
import subprocess
import requests
import xml.etree.ElementTree as ET


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# d6flipflop/
PROJECT_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..")
)

# d6flipflop/templates/
TEMPLATE_DIR = os.path.join(
    PROJECT_DIR,
    "templates"
)


# ============================================================
# FLASK APP
# ============================================================

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR
)


# ============================================================
# PROJECT FILES
# ============================================================

DESIGN_FILE = os.path.join(
    PROJECT_DIR,
    "flipflop.sv"
)

TESTBENCH_FILE = os.path.join(
    PROJECT_DIR,
    "testbench_flipflop.py"
)

SYNTH_FILE = os.path.join(
    PROJECT_DIR,
    "synth.ys"
)

MAKEFILE_PATH = os.path.join(
    PROJECT_DIR,
    "Makefile"
)


# Generated files

RESULTS_FILE = os.path.join(
    PROJECT_DIR,
    "results.xml"
)

VCD_FILE = os.path.join(
    PROJECT_DIR,
    "dff_waveform.vcd"
)

NETLIST_FILE = os.path.join(
    PROJECT_DIR,
    "dff_netlist.v"
)

DOT_FILE = os.path.join(
    PROJECT_DIR,
    "dff_synth.dot"
)

PNG_FILE = os.path.join(
    PROJECT_DIR,
    "dff_synth.png"
)


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_BASE_URL = "http://127.0.0.1:11434"

OLLAMA_GENERATE_URL = (
    f"{OLLAMA_BASE_URL}/api/generate"
)

OLLAMA_TAGS_URL = (
    f"{OLLAMA_BASE_URL}/api/tags"
)

# IMPORTANT:
# Run: ollama list
# Change this to your exact model name if required.
OLLAMA_MODEL = "llama3.2"


# ============================================================
# READ FILE
# ============================================================

def read_file(file_path):

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:

        return file.read()


# ============================================================
# CHECK OLLAMA
# ============================================================

def check_ollama():

    try:

        response = requests.get(
            OLLAMA_TAGS_URL,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        models = []

        for model in data.get("models", []):

            models.append(
                model.get("name", "")
            )

        return {
            "status": "PASS",
            "available": True,
            "models": models
        }

    except Exception as error:

        return {
            "status": "ERROR",
            "available": False,
            "models": [],
            "error": str(error)
        }


# ============================================================
# OLLAMA AI REVIEW
# ============================================================

def ollama_review(
    file_name,
    code,
    file_type
):

    prompt = f"""
You are an expert VLSI engineer.

You specialize in:

- Verilog
- SystemVerilog
- RTL Design
- Digital Logic
- Flip-Flops
- Cocotb
- Icarus Verilog
- Yosys
- RTL Simulation
- RTL Synthesis
- Hardware Verification

Review this file carefully.

FILE NAME:
{file_name}

FILE TYPE:
{file_type}


CHECK FOR:

1. Syntax errors
2. Functional errors
3. RTL design issues
4. Reset behavior
5. Clock behavior
6. Race conditions
7. Latch inference
8. Simulation problems
9. Synthesis problems
10. Testbench quality
11. Missing test cases
12. Code quality


Return your answer in EXACTLY this format:


STATUS: PASS or FAIL

ISSUES:
- List all issues found.
- If no issues exist write:
  No major issues found.

SUGGESTIONS:
- List improvements.

SUMMARY:
- Give a short technical summary.


If there is a major functional,
syntax, simulation or synthesis problem,
use:

STATUS: FAIL


FILE CONTENT:

------------------------------------------------

{code}

------------------------------------------------
"""

    try:

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(
            OLLAMA_GENERATE_URL,
            json=payload,
            timeout=180
        )

        response.raise_for_status()

        data = response.json()

        review = data.get(
            "response",
            "No response received from Ollama."
        )

        review_upper = review.upper()

        if "STATUS: FAIL" in review_upper:

            status = "FAIL"

        elif "STATUS: PASS" in review_upper:

            status = "PASS"

        else:

            status = "PASS"

        return {
            "status": status,
            "review": review
        }

    except requests.exceptions.ConnectionError:

        return {
            "status": "ERROR",
            "review": (
                "Cannot connect to Ollama.\n"
                "Run: ollama serve"
            )
        }

    except requests.exceptions.Timeout:

        return {
            "status": "ERROR",
            "review": "Ollama request timed out."
        }

    except requests.exceptions.HTTPError as error:

        return {
            "status": "ERROR",
            "review": f"Ollama HTTP error: {error}"
        }

    except Exception as error:

        return {
            "status": "ERROR",
            "review": str(error)
        }


# ============================================================
# SYSTEMVERILOG REVIEW
# ============================================================

def review_systemverilog():

    try:

        code = read_file(DESIGN_FILE)

        result = ollama_review(
            "flipflop.sv",
            code,
            "SystemVerilog RTL Design"
        )

        return {
            "stage": "SystemVerilog AI Review",
            "file": "flipflop.sv",
            "status": result["status"],
            "review": result["review"]
        }

    except Exception as error:

        return {
            "stage": "SystemVerilog AI Review",
            "file": "flipflop.sv",
            "status": "ERROR",
            "review": str(error)
        }


# ============================================================
# TESTBENCH REVIEW
# ============================================================

def review_testbench():

    try:

        code = read_file(TESTBENCH_FILE)

        result = ollama_review(
            "testbench_flipflop.py",
            code,
            "Python Cocotb Testbench"
        )

        return {
            "stage": "Cocotb Testbench AI Review",
            "file": "testbench_flipflop.py",
            "status": result["status"],
            "review": result["review"]
        }

    except Exception as error:

        return {
            "stage": "Cocotb Testbench AI Review",
            "file": "testbench_flipflop.py",
            "status": "ERROR",
            "review": str(error)
        }


# ============================================================
# YOSYS REVIEW
# ============================================================

def review_yosys():

    try:

        code = read_file(SYNTH_FILE)

        result = ollama_review(
            "synth.ys",
            code,
            "Yosys Synthesis Script"
        )

        return {
            "stage": "Yosys Script AI Review",
            "file": "synth.ys",
            "status": result["status"],
            "review": result["review"]
        }

    except Exception as error:

        return {
            "stage": "Yosys Script AI Review",
            "file": "synth.ys",
            "status": "ERROR",
            "review": str(error)
        }


# ============================================================
# MAKEFILE REVIEW
# ============================================================

def review_makefile():

    try:

        code = read_file(MAKEFILE_PATH)

        result = ollama_review(
            "Makefile",
            code,
            "Build file for Cocotb and Yosys"
        )

        return {
            "stage": "Makefile AI Review",
            "file": "Makefile",
            "status": result["status"],
            "review": result["review"]
        }

    except Exception as error:

        return {
            "stage": "Makefile AI Review",
            "file": "Makefile",
            "status": "ERROR",
            "review": str(error)
        }


# ============================================================
# REMOVE OLD GENERATED FILES
# ============================================================

def remove_old_artifacts():

    files = [

        RESULTS_FILE,
        VCD_FILE,
        NETLIST_FILE,
        DOT_FILE,
        PNG_FILE

    ]

    for file_path in files:

        if os.path.exists(file_path):

            try:

                os.remove(file_path)

            except Exception:

                pass


# ============================================================
# RUN MAKE
# ============================================================

def run_make():

    try:

        remove_old_artifacts()

        result = subprocess.run(
            ["make"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=300
        )

        output = (
            result.stdout
            + "\n"
            + result.stderr
        )

        status = (
            "PASS"
            if result.returncode == 0
            else "FAIL"
        )

        return {
            "stage": "Build and Simulation",
            "status": status,
            "return_code": result.returncode,
            "output": output
        }

    except subprocess.TimeoutExpired:

        return {
            "stage": "Build and Simulation",
            "status": "ERROR",
            "return_code": -1,
            "output": "make command timed out."
        }

    except Exception as error:

        return {
            "stage": "Build and Simulation",
            "status": "ERROR",
            "return_code": -1,
            "output": str(error)
        }


# ============================================================
# VALIDATE COCOTB RESULTS
# ============================================================

def validate_simulation():

    vcd_exists = os.path.exists(VCD_FILE)

    if not os.path.exists(RESULTS_FILE):

        return {
            "stage": "Simulation Validation",
            "status": "FAIL",
            "details": "results.xml was not generated.",
            "tests": 0,
            "failures": 0,
            "errors": 0,
            "vcd_generated": vcd_exists
        }

    try:

        tree = ET.parse(RESULTS_FILE)

        root = tree.getroot()

        if root.tag == "testsuite":

            suites = [root]

        else:

            suites = root.findall(".//testsuite")

        tests = 0
        failures = 0
        errors = 0

        for suite in suites:

            tests += int(
                suite.attrib.get("tests", 0)
            )

            failures += int(
                suite.attrib.get("failures", 0)
            )

            errors += int(
                suite.attrib.get("errors", 0)
            )

        if failures > 0 or errors > 0:

            status = "FAIL"

            details = (
                f"{failures} failure(s), "
                f"{errors} error(s) "
                f"out of {tests} test(s)."
            )

        else:

            status = "PASS"

            details = (
                f"All {tests} Cocotb "
                f"test(s) passed successfully."
            )

        return {

            "stage": "Simulation Validation",

            "status": status,

            "details": details,

            "tests": tests,

            "failures": failures,

            "errors": errors,

            "vcd_file": "dff_waveform.vcd",

            "vcd_generated": vcd_exists
        }

    except Exception as error:

        return {

            "stage": "Simulation Validation",

            "status": "ERROR",

            "details": str(error),

            "tests": 0,

            "failures": 0,

            "errors": 0,

            "vcd_generated": vcd_exists
        }


# ============================================================
# VALIDATE GENERATED FILES
# ============================================================

def validate_artifacts():

    vcd_exists = os.path.exists(VCD_FILE)

    netlist_exists = os.path.exists(NETLIST_FILE)

    dot_exists = os.path.exists(DOT_FILE)

    png_exists = os.path.exists(PNG_FILE)

    all_exist = (

        vcd_exists
        and netlist_exists
        and dot_exists
        and png_exists

    )

    return {

        "stage": "Generated Files Validation",

        "status": (
            "PASS"
            if all_exist
            else "FAIL"
        ),

        "vcd": {
            "file": "dff_waveform.vcd",
            "generated": vcd_exists
        },

        "netlist": {
            "file": "dff_netlist.v",
            "generated": netlist_exists
        },

        "dot": {
            "file": "dff_synth.dot",
            "generated": dot_exists
        },

        "png": {
            "file": "dff_synth.png",
            "generated": png_exists
        }
    }


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def index():

    return render_template("index.html")


# ============================================================
# API - OLLAMA STATUS
# ============================================================

@app.route("/api/ollama_status")
def api_ollama_status():

    return jsonify(check_ollama())


# ============================================================
# API - SYSTEMVERILOG REVIEW
# ============================================================

@app.route(
    "/api/review/systemverilog",
    methods=["POST"]
)
def api_systemverilog_review():

    return jsonify(
        review_systemverilog()
    )


# ============================================================
# API - TESTBENCH REVIEW
# ============================================================

@app.route(
    "/api/review/testbench",
    methods=["POST"]
)
def api_testbench_review():

    return jsonify(
        review_testbench()
    )


# ============================================================
# API - YOSYS REVIEW
# ============================================================

@app.route(
    "/api/review/yosys",
    methods=["POST"]
)
def api_yosys_review():

    return jsonify(
        review_yosys()
    )


# ============================================================
# API - MAKEFILE REVIEW
# ============================================================

@app.route(
    "/api/review/makefile",
    methods=["POST"]
)
def api_makefile_review():

    return jsonify(
        review_makefile()
    )


# ============================================================
# API - RUN MAKE
# ============================================================

@app.route(
    "/api/run",
    methods=["POST"]
)
def api_run():

    try:

        make_result = run_make()

        simulation_result = (
            validate_simulation()
        )

        artifacts_result = (
            validate_artifacts()
        )

        return jsonify({

            "status": "SUCCESS",

            "make_execution":
                make_result,

            "simulation":
                simulation_result,

            "artifacts":
                artifacts_result
        })

    except Exception as error:

        return jsonify({

            "status": "ERROR",

            "error": str(error)

        }), 500


# ============================================================
# API - COMPLETE PIPELINE
# ============================================================

@app.route(
    "/api/run_pipeline",
    methods=["POST"]
)
def api_run_pipeline():

    try:

        ollama_info = check_ollama()

        systemverilog_review = (
            review_systemverilog()
        )

        testbench_review = (
            review_testbench()
        )

        yosys_review = (
            review_yosys()
        )

        makefile_review = (
            review_makefile()
        )

        make_result = run_make()

        simulation_result = (
            validate_simulation()
        )

        artifacts_result = (
            validate_artifacts()
        )

        return jsonify({

            "status": "SUCCESS",

            "ollama": ollama_info,

            "systemverilog_review":
                systemverilog_review,

            "testbench_review":
                testbench_review,

            "yosys_review":
                yosys_review,

            "makefile_review":
                makefile_review,

            "make_execution":
                make_result,

            "simulation":
                simulation_result,

            "artifacts":
                artifacts_result

        })

    except Exception as error:

        return jsonify({

            "status": "ERROR",

            "error": str(error)

        }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print("\n==========================================")
    print(" AI EDA FLIP-FLOP VALIDATION SERVER")
    print("==========================================\n")

    print("Project:", PROJECT_DIR)
    print("Templates:", TEMPLATE_DIR)
    print("Ollama Model:", OLLAMA_MODEL)

    print("\nOpen:")
    print("http://127.0.0.1:5000\n")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )