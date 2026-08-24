from flask import Flask, jsonify, render_template
import os
import subprocess
import requests
import xml.etree.ElementTree as ET


# ============================================================
# PATH CONFIGURATION
# ============================================================

# backend/app.py directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Parent project directory: d6flipflop/
PROJECT_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..")
)

# templates directory is directly under d6flipflop/
TEMPLATE_DIR = os.path.join(
    PROJECT_DIR,
    "templates"
)


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR
)


# ============================================================
# PROJECT FILE PATHS
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

MAKEFILE = os.path.join(
    PROJECT_DIR,
    "Makefile"
)

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

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

# Change this if you use another Ollama model
OLLAMA_MODEL = "llama3.2"


# ============================================================
# HELPER: READ FILE
# ============================================================

def read_project_file(file_path):
    """
    Read a project file safely.
    """

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
# CHECK OLLAMA SERVER
# ============================================================

def check_ollama():

    try:

        response = requests.get(
            "http://127.0.0.1:11434/api/tags",
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        models = [
            model.get("name", "")
            for model in data.get("models", [])
        ]

        return {
            "available": True,
            "models": models
        }

    except Exception as error:

        return {
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
    review_type
):

    prompt = f"""
You are a senior VLSI RTL design, verification,
SystemVerilog, Cocotb and Yosys expert.

Review the following file carefully.

FILE NAME:
{file_name}

FILE TYPE:
{review_type}

You must check:

1. Syntax correctness
2. Functional correctness
3. RTL design issues
4. Reset behavior
5. Clock behavior
6. Race conditions
7. Simulation compatibility
8. Synthesis compatibility
9. Verification coverage
10. Code quality

Return your answer EXACTLY in this format:

STATUS: PASS or FAIL

ISSUES:
- List all problems found.
- If no issue exists, write: No major issues found.

SUGGESTIONS:
- List improvements.

SUMMARY:
Give a technical explanation of the review.

FILE CONTENT:
----------------------------------------

{code}

----------------------------------------
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=180
        )

        response.raise_for_status()

        data = response.json()

        review_text = data.get(
            "response",
            "No response received from Ollama."
        )

        review_upper = review_text.upper()

        # Default status
        status = "PASS"

        # Detect explicit FAIL
        if "STATUS: FAIL" in review_upper:
            status = "FAIL"

        return {
            "status": status,
            "review": review_text
        }

    except requests.exceptions.ConnectionError:

        return {
            "status": "ERROR",
            "review": (
                "Cannot connect to Ollama.\n"
                "Start Ollama using:\n"
                "ollama serve"
            )
        }

    except requests.exceptions.Timeout:

        return {
            "status": "ERROR",
            "review": (
                "Ollama request timed out."
            )
        }

    except requests.exceptions.HTTPError as error:

        return {
            "status": "ERROR",
            "review": (
                f"Ollama HTTP error: {error}"
            )
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

        code = read_project_file(
            DESIGN_FILE
        )

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
# COCOTB TESTBENCH REVIEW
# ============================================================

def review_testbench():

    try:

        code = read_project_file(
            TESTBENCH_FILE
        )

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
# YOSYS SCRIPT REVIEW
# ============================================================

def review_yosys():

    try:

        code = read_project_file(
            SYNTH_FILE
        )

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

        code = read_project_file(
            MAKEFILE
        )

        result = ollama_review(
            "Makefile",
            code,
            "Makefile for Cocotb, Icarus and Yosys"
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
# DELETE OLD GENERATED FILES
# ============================================================

def remove_old_artifacts():

    files = [
        RESULTS_FILE,
        VCD_FILE,
        NETLIST_FILE,
        DOT_FILE,
        PNG_FILE
    ]

    removed_files = []

    for file_path in files:

        if os.path.exists(file_path):

            try:

                os.remove(file_path)

                removed_files.append(
                    os.path.basename(file_path)
                )

            except Exception:
                pass

    return removed_files


# ============================================================
# RUN MAKE
# ============================================================

def run_make():

    try:

        # Remove old generated files so validation
        # does not incorrectly report old files.
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

        if result.returncode == 0:

            status = "PASS"

        else:

            status = "FAIL"

        return {
            "stage": "Build, Simulation and Synthesis",
            "status": status,
            "return_code": result.returncode,
            "output": output
        }

    except subprocess.TimeoutExpired:

        return {
            "stage": "Build, Simulation and Synthesis",
            "status": "ERROR",
            "return_code": -1,
            "output": (
                "make command timed out."
            )
        }

    except Exception as error:

        return {
            "stage": "Build, Simulation and Synthesis",
            "status": "ERROR",
            "return_code": -1,
            "output": str(error)
        }


# ============================================================
# VALIDATE RESULTS.XML
# ============================================================

def validate_simulation():

    vcd_exists = os.path.exists(
        VCD_FILE
    )

    if not os.path.exists(RESULTS_FILE):

        return {
            "stage": "Cocotb Simulation Validation",
            "status": "FAIL",
            "details": (
                "results.xml was not generated."
            ),
            "tests": 0,
            "failures": 0,
            "errors": 0,
            "vcd_file": "dff_waveform.vcd",
            "vcd_generated": vcd_exists
        }

    try:

        tree = ET.parse(
            RESULTS_FILE
        )

        root = tree.getroot()

        # results.xml may have either:
        # <testsuite>
        # or
        # <testsuites>

        if root.tag == "testsuite":

            suites = [root]

        else:

            suites = root.findall(
                ".//testsuite"
            )

        total_tests = 0
        failures = 0
        errors = 0

        for suite in suites:

            total_tests += int(
                suite.attrib.get(
                    "tests",
                    0
                )
            )

            failures += int(
                suite.attrib.get(
                    "failures",
                    0
                )
            )

            errors += int(
                suite.attrib.get(
                    "errors",
                    0
                )
            )

        if failures > 0 or errors > 0:

            status = "FAIL"

            details = (
                f"Simulation completed with "
                f"{failures} failure(s) and "
                f"{errors} error(s) out of "
                f"{total_tests} test(s)."
            )

        else:

            status = "PASS"

            details = (
                f"All {total_tests} Cocotb "
                f"test(s) passed successfully."
            )

        return {
            "stage": "Cocotb Simulation Validation",
            "status": status,
            "details": details,
            "tests": total_tests,
            "failures": failures,
            "errors": errors,
            "vcd_file": "dff_waveform.vcd",
            "vcd_generated": vcd_exists
        }

    except Exception as error:

        return {
            "stage": "Cocotb Simulation Validation",
            "status": "ERROR",
            "details": str(error),
            "tests": 0,
            "failures": 0,
            "errors": 0,
            "vcd_file": "dff_waveform.vcd",
            "vcd_generated": vcd_exists
        }


# ============================================================
# VALIDATE GENERATED ARTIFACTS
# ============================================================

def validate_artifacts():

    vcd_exists = os.path.exists(
        VCD_FILE
    )

    netlist_exists = os.path.exists(
        NETLIST_FILE
    )

    dot_exists = os.path.exists(
        DOT_FILE
    )

    png_exists = os.path.exists(
        PNG_FILE
    )

    all_generated = (
        vcd_exists
        and netlist_exists
        and dot_exists
        and png_exists
    )

    if all_generated:

        status = "PASS"

    else:

        status = "FAIL"

    return {
        "stage": "Generated Artifacts Validation",
        "status": status,

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

    return render_template(
        "index.html"
    )


# ============================================================
# API: CHECK OLLAMA
# ============================================================

@app.route(
    "/api/ollama_status",
    methods=["GET"]
)
def ollama_status():

    return jsonify(
        check_ollama()
    )


# ============================================================
# API: REVIEW SYSTEMVERILOG
# ============================================================

@app.route(
    "/api/review/systemverilog",
    methods=["POST"]
)
def api_review_systemverilog():

    return jsonify(
        review_systemverilog()
    )


# ============================================================
# API: REVIEW TESTBENCH
# ============================================================

@app.route(
    "/api/review/testbench",
    methods=["POST"]
)
def api_review_testbench():

    return jsonify(
        review_testbench()
    )


# ============================================================
# API: REVIEW YOSYS
# ============================================================

@app.route(
    "/api/review/yosys",
    methods=["POST"]
)
def api_review_yosys():

    return jsonify(
        review_yosys()
    )


# ============================================================
# API: REVIEW MAKEFILE
# ============================================================

@app.route(
    "/api/review/makefile",
    methods=["POST"]
)
def api_review_makefile():

    return jsonify(
        review_makefile()
    )


# ============================================================
# API: RUN SIMULATION / MAKE
# ============================================================

@app.route(
    "/api/run",
    methods=["POST"]
)
def api_run():

    make_result = run_make()

    simulation_result = validate_simulation()

    artifacts_result = validate_artifacts()

    return jsonify({

        "make_execution": make_result,

        "simulation": simulation_result,

        "artifacts": artifacts_result

    })


# ============================================================
# API: RUN COMPLETE PIPELINE
# ============================================================

@app.route(
    "/api/run_pipeline",
    methods=["POST"]
)
def api_run_pipeline():

    # Check Ollama first
    ollama_info = check_ollama()

    # AI Reviews
    systemverilog_review = review_systemverilog()

    testbench_review = review_testbench()

    yosys_review = review_yosys()

    makefile_review = review_makefile()

    # Execute simulation and synthesis
    make_result = run_make()

    # Validate simulation
    simulation_result = validate_simulation()

    # Validate generated files
    artifacts_result = validate_artifacts()

    return jsonify({

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


# ============================================================
# START FLASK SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("==========================================")
    print(" AI EDA FLIP-FLOP VALIDATION SERVER")
    print("==========================================")
    print(f"Project Directory : {PROJECT_DIR}")
    print(f"Template Directory: {TEMPLATE_DIR}")
    print(f"Design File       : {DESIGN_FILE}")
    print(f"Testbench File    : {TESTBENCH_FILE}")
    print(f"Yosys File        : {SYNTH_FILE}")
    print(f"Ollama URL        : {OLLAMA_URL}")
    print(f"Ollama Model      : {OLLAMA_MODEL}")
    print("==========================================")
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )