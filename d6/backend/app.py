from flask import Flask, jsonify, render_template
import os
import subprocess
import requests


# =========================================================
# PATH CONFIGURATION
# =========================================================

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_DIR = os.path.abspath(
    os.path.join(BACKEND_DIR, "..")
)

TEMPLATE_DIR = os.path.join(
    PROJECT_DIR,
    "templates"
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR
)


# =========================================================
# PROJECT FILES
# =========================================================

DESIGN_PATH = os.path.join(
    PROJECT_DIR,
    "decoder_2to4.sv"
)

TESTBENCH_PATH = os.path.join(
    PROJECT_DIR,
    "testbench_decoder_2to4.py"
)

MAKEFILE_PATH = os.path.join(
    PROJECT_DIR,
    "Makefile"
)

NETLIST_PATH = os.path.join(
    PROJECT_DIR,
    "decoder_2to4_netlist.v"
)

VCD_PATH = os.path.join(
    PROJECT_DIR,
    "decoder_2to4.vcd"
)

PNG_PATH = os.path.join(
    PROJECT_DIR,
    "decoder_2to4.png"
)


# =========================================================
# OLLAMA CONFIGURATION
# =========================================================

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

OLLAMA_MODEL = "llama3.2"


# =========================================================
# HELPER FUNCTION
# =========================================================

def read_file(file_path):

    with open(file_path, "r") as file:

        return file.read()


# =========================================================
# OLLAMA API
# =========================================================

def ask_ollama(prompt):

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

        ai_response = data.get(
            "response",
            "No response received from Ollama."
        )

        # Convert response to uppercase for checking
        response_upper = ai_response.upper()

        # IMPORTANT:
        # Ollama may say STATUS: FAIL even though
        # the API request itself succeeded.
        if "STATUS: FAIL" in response_upper:

            status = "FAIL"

        elif "STATUS: PASS" in response_upper:

            status = "PASS"

        else:

            status = "WARNING"

        return {

            "status": status,

            "details": ai_response

        }


    except requests.exceptions.ConnectionError:

        return {

            "status": "ERROR",

            "details": (
                "Cannot connect to Ollama. "
                "Please start Ollama using: ollama serve"
            )

        }


    except requests.exceptions.Timeout:

        return {

            "status": "ERROR",

            "details": "Ollama request timed out."

        }


    except Exception as error:

        return {

            "status": "ERROR",

            "details": str(error)

        }


# =========================================================
# SYSTEMVERILOG REVIEW
# =========================================================

def review_systemverilog():

    try:

        design_code = read_file(DESIGN_PATH)

        prompt = f"""
You are an expert RTL, Verilog and SystemVerilog verification engineer.

Review the following SystemVerilog design.

Check carefully for:

1. Syntax errors
2. Functional correctness
3. Decoder functionality
4. Incorrect output mapping
5. Bit width problems
6. Latch inference
7. Combinational logic issues
8. Case statement problems
9. Synthesizability
10. General RTL coding issues

The module should behave as a 2-to-4 decoder.

Expected behavior:

00 -> 0001
01 -> 0010
10 -> 0100
11 -> 1000

Return your answer EXACTLY in this format:

STATUS: PASS

ISSUES:
- None

SUGGESTIONS:
- Optional suggestions

OR if problems exist:

STATUS: FAIL

ISSUES:
- Describe each real problem

SUGGESTIONS:
- Explain how to fix each problem

Do not report imaginary problems.

SYSTEMVERILOG CODE:

{design_code}
"""

        result = ask_ollama(prompt)

        return {

            "file": "decoder_2to4.sv",

            "stage": "SystemVerilog Review",

            "status": result["status"],

            "details": result["details"]

        }


    except Exception as error:

        return {

            "stage": "SystemVerilog Review",

            "status": "ERROR",

            "details": str(error)

        }


# =========================================================
# TESTBENCH REVIEW
# =========================================================

def review_testbench():

    try:

        testbench_code = read_file(TESTBENCH_PATH)

        prompt = f"""
You are an expert Python and Cocotb verification engineer.

Review the following Cocotb testbench.

Check carefully for:

1. Python syntax
2. Cocotb API correctness
3. Test coverage
4. Expected output correctness
5. Assertions
6. Timing
7. Missing test cases
8. Incorrect DUT signal usage
9. Verification quality

The DUT is a 2-to-4 decoder.

Expected mapping:

00 -> 0001
01 -> 0010
10 -> 0100
11 -> 1000

Return EXACTLY:

STATUS: PASS

ISSUES:
- None

SUGGESTIONS:
- Optional suggestions

OR:

STATUS: FAIL

ISSUES:
- Real issue

SUGGESTIONS:
- Fix

Do not invent problems.

TESTBENCH CODE:

{testbench_code}
"""

        result = ask_ollama(prompt)

        return {

            "file": "testbench_decoder_2to4.py",

            "stage": "Testbench Review",

            "status": result["status"],

            "details": result["details"]

        }


    except Exception as error:

        return {

            "stage": "Testbench Review",

            "status": "ERROR",

            "details": str(error)

        }


# =========================================================
# MAKEFILE REVIEW
# =========================================================

def review_makefile():

    try:

        makefile_code = read_file(MAKEFILE_PATH)

        prompt = f"""
You are an expert in:

- GNU Make
- Cocotb
- Icarus Verilog
- SystemVerilog
- Yosys

Review this Makefile.

The expected flow is:

1. Run Cocotb simulation
2. Generate VCD waveform
3. Generate synthesized Verilog netlist
4. Generate PNG schematic
5. Clean generated files

Check:

1. Makefile syntax
2. Target dependencies
3. Cocotb integration
4. Icarus Verilog integration
5. Yosys commands
6. Incorrect paths
7. Missing targets
8. Potential errors

Return EXACTLY:

STATUS: PASS

ISSUES:
- None

SUGGESTIONS:
- Optional

OR:

STATUS: FAIL

ISSUES:
- Problem

SUGGESTIONS:
- Fix

Do not invent problems.

MAKEFILE:

{makefile_code}
"""

        result = ask_ollama(prompt)

        return {

            "file": "Makefile",

            "stage": "Makefile Review",

            "status": result["status"],

            "details": result["details"]

        }


    except Exception as error:

        return {

            "stage": "Makefile Review",

            "status": "ERROR",

            "details": str(error)

        }


# =========================================================
# RUN SIMULATION
# =========================================================

def run_simulation():

    try:

        result = subprocess.run(

            ["make", "run"],

            cwd=PROJECT_DIR,

            capture_output=True,

            text=True,

            timeout=180
        )

        output = (
            result.stdout
            +
            "\n"
            +
            result.stderr
        )

        if result.returncode == 0:

            return {

                "stage": "Simulation",

                "status": "PASS",

                "details":
                    "Cocotb simulation completed successfully.",

                "output": output

            }


        return {

            "stage": "Simulation",

            "status": "FAIL",

            "details":
                "Simulation failed. Check output for details.",

            "output": output

        }


    except subprocess.TimeoutExpired:

        return {

            "stage": "Simulation",

            "status": "ERROR",

            "details":
                "Simulation timed out."

        }


    except Exception as error:

        return {

            "stage": "Simulation",

            "status": "ERROR",

            "details": str(error)

        }


# =========================================================
# GENERATE NETLIST
# =========================================================

def generate_netlist():

    try:

        result = subprocess.run(

            ["make", "netlist"],

            cwd=PROJECT_DIR,

            capture_output=True,

            text=True,

            timeout=180
        )

        output = result.stdout + "\n" + result.stderr

        if (
            result.returncode == 0
            and os.path.exists(NETLIST_PATH)
        ):

            return {

                "stage": "Netlist Generation",

                "status": "PASS",

                "details":
                    "Netlist generated successfully.",

                "output": output

            }


        return {

            "stage": "Netlist Generation",

            "status": "FAIL",

            "details":
                "Netlist generation failed.",

            "output": output

        }


    except Exception as error:

        return {

            "stage": "Netlist Generation",

            "status": "ERROR",

            "details": str(error)

        }


# =========================================================
# REVIEW NETLIST WITH OLLAMA
# =========================================================

def review_netlist():

    try:

        if not os.path.exists(NETLIST_PATH):

            return {

                "file": "decoder_2to4_netlist.v",

                "stage": "Netlist Review",

                "status": "FAIL",

                "details":
                    "Netlist does not exist. Generate it first."

            }

        netlist_code = read_file(NETLIST_PATH)

        prompt = f"""
You are an expert ASIC synthesis and RTL engineer.

Review this synthesized Verilog netlist.

Check:

1. Syntax
2. Module existence
3. Logic structure
4. Output connections
5. Obvious synthesis problems

The original design should implement a 2-to-4 decoder.

Return EXACTLY:

STATUS: PASS

ISSUES:
- None

SUGGESTIONS:
- Optional

OR:

STATUS: FAIL

ISSUES:
- Problem

SUGGESTIONS:
- Fix

NETLIST:

{netlist_code}
"""

        result = ask_ollama(prompt)

        return {

            "file": "decoder_2to4_netlist.v",

            "stage": "Netlist Review",

            "status": result["status"],

            "details": result["details"]

        }


    except Exception as error:

        return {

            "stage": "Netlist Review",

            "status": "ERROR",

            "details": str(error)

        }


# =========================================================
# GENERATE PNG
# =========================================================

def generate_png():

    try:

        result = subprocess.run(

            ["make", "png"],

            cwd=PROJECT_DIR,

            capture_output=True,

            text=True,

            timeout=180
        )

        output = result.stdout + "\n" + result.stderr

        if result.returncode == 0:

            return {

                "stage": "PNG Generation",

                "status": "PASS",

                "details":
                    "Schematic PNG generated successfully.",

                "output": output

            }


        return {

            "stage": "PNG Generation",

            "status": "FAIL",

            "details":
                "PNG generation failed.",

            "output": output

        }


    except Exception as error:

        return {

            "stage": "PNG Generation",

            "status": "ERROR",

            "details": str(error)

        }


# =========================================================
# VALIDATE VCD
# =========================================================

def validate_vcd():

    try:

        if not os.path.exists(VCD_PATH):

            return {

                "file": "decoder_2to4.vcd",

                "stage": "VCD Validation",

                "status": "FAIL",

                "details":
                    "VCD file does not exist. Run simulation first."

            }

        size = os.path.getsize(VCD_PATH)

        if size == 0:

            return {

                "file": "decoder_2to4.vcd",

                "stage": "VCD Validation",

                "status": "FAIL",

                "details":
                    "VCD file exists but is empty."

            }

        return {

            "file": "decoder_2to4.vcd",

            "stage": "VCD Validation",

            "status": "PASS",

            "details":
                f"VCD generated successfully. File size: {size} bytes."

        }


    except Exception as error:

        return {

            "stage": "VCD Validation",

            "status": "ERROR",

            "details": str(error)

        }


# =========================================================
# VALIDATE PNG
# =========================================================

def validate_png():

    try:

        if not os.path.exists(PNG_PATH):

            return {

                "file": "decoder_2to4.png",

                "stage": "PNG Validation",

                "status": "FAIL",

                "details":
                    "PNG schematic does not exist. Generate it first."

            }

        size = os.path.getsize(PNG_PATH)

        if size == 0:

            return {

                "file": "decoder_2to4.png",

                "stage": "PNG Validation",

                "status": "FAIL",

                "details":
                    "PNG file exists but is empty."

            }

        return {

            "file": "decoder_2to4.png",

            "stage": "PNG Validation",

            "status": "PASS",

            "details":
                f"PNG schematic generated successfully. File size: {size} bytes."

        }


    except Exception as error:

        return {

            "stage": "PNG Validation",

            "status": "ERROR",

            "details": str(error)

        }


# =========================================================
# GENERATE EVERYTHING
# =========================================================

def generate_all():

    try:

        result = subprocess.run(

            ["make"],

            cwd=PROJECT_DIR,

            capture_output=True,

            text=True,

            timeout=300
        )

        output = result.stdout + "\n" + result.stderr

        if result.returncode == 0:

            return {

                "stage": "Generate All Files",

                "status": "PASS",

                "details":
                    "Simulation, netlist and PNG generation completed.",

                "output": output

            }

        return {

            "stage": "Generate All Files",

            "status": "FAIL",

            "details":
                "Make command failed.",

            "output": output

        }


    except Exception as error:

        return {

            "stage": "Generate All Files",

            "status": "ERROR",

            "details": str(error)

        }


# =========================================================
# FLASK ROUTES
# =========================================================

@app.route("/")
def index():

    return render_template("index.html")


@app.route("/review/systemverilog", methods=["POST"])
def systemverilog_review():

    return jsonify(review_systemverilog())


@app.route("/review/testbench", methods=["POST"])
def testbench_review():

    return jsonify(review_testbench())


@app.route("/review/makefile", methods=["POST"])
def makefile_review():

    return jsonify(review_makefile())


@app.route("/run/simulation", methods=["POST"])
def simulation():

    return jsonify(run_simulation())


@app.route("/validate/vcd", methods=["POST"])
def vcd():

    return jsonify(validate_vcd())


@app.route("/review/netlist", methods=["POST"])
def netlist():

    return jsonify(review_netlist())


@app.route("/validate/png", methods=["POST"])
def png():

    return jsonify(validate_png())


@app.route("/generate/all", methods=["POST"])
def generate():

    return jsonify(generate_all())


@app.route("/validate_all", methods=["POST"])
def validate_all():

    results = {}

    # AI reviews
    results["systemverilog_review"] = review_systemverilog()

    results["testbench_review"] = review_testbench()

    results["makefile_review"] = review_makefile()

    # Actual EDA execution
    results["simulation"] = run_simulation()

    # Generate artifacts
    results["netlist_generation"] = generate_netlist()

    results["png_generation"] = generate_png()

    # Validate generated files
    results["vcd_validation"] = validate_vcd()

    results["netlist_review"] = review_netlist()

    results["png_validation"] = validate_png()

    return jsonify(results)


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )