from flask import Flask, request, jsonify, render_template
import subprocess
import os
import json
import xml.etree.ElementTree as ET

from openai import OpenAI


app = Flask(
    __name__,
    template_folder="../templates"
)


# ============================================================
# OPENAI CLIENT
# ============================================================

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is not set. "
        "Add it to ~/.bashrc and run: source ~/.bashrc"
    )

client = OpenAI(
    api_key=api_key
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..")
)

DESIGN_PATH = os.path.join(
    PROJECT_DIR,
    "decoder_2to4.sv"
)

TESTBENCH_PATH = os.path.join(
    PROJECT_DIR,
    "testbench_decoder_2to4.py"
)

RESULTS_PATH = os.path.join(
    PROJECT_DIR,
    "results.xml"
)


# ============================================================
# HELPER FUNCTION
# ============================================================

def parse_ai_json(text: str) -> dict:
    """
    Parse JSON returned by the AI.
    Handles cases where markdown code fences are returned.
    """

    text = text.strip()

    if text.startswith("```"):

        lines = text.splitlines()

        # Remove first line: ```json or ```
        lines = lines[1:]

        # Remove last ``` if present
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines)

    return json.loads(text)


# ============================================================
# AI DESIGN REVIEW
# ============================================================

def ai_design_review(design_code: str) -> dict:

    prompt = f"""
You are an expert VLSI RTL and SystemVerilog engineer.

Review the following SystemVerilog design for a 2-to-4 decoder.

Check carefully for:

1. Syntax errors
2. Compilation errors
3. Incorrect decoder logic
4. Incorrect output mapping
5. Signal width problems
6. Inferred latches
7. Combinational logic problems
8. Synthesizability problems
9. Simulation problems

A PASS should only be returned if the code is logically correct
for a 2-to-4 decoder and has no important issues.

Return ONLY valid JSON.

Use exactly this format:

{{
    "status": "PASS or FAIL",
    "details": "Short explanation",
    "issues": [
        "Issue 1",
        "Issue 2"
    ]
}}

If there are no issues:

{{
    "status": "PASS",
    "details": "Design is valid.",
    "issues": []
}}

SystemVerilog code:

{design_code}
"""

    try:

        response = client.responses.create(
            model="gpt-5",
            input=prompt
        )

        result = parse_ai_json(
            response.output_text
        )

        return {
            "stage": "Design Review",
            "status": result.get(
                "status",
                "FAIL"
            ),
            "details": result.get(
                "details",
                ""
            ),
            "issues": result.get(
                "issues",
                []
            )
        }

    except Exception as e:

        return {
            "stage": "Design Review",
            "status": "FAIL",
            "details": f"AI review failed: {str(e)}",
            "issues": []
        }


# ============================================================
# AI TESTBENCH REVIEW
# ============================================================

def ai_testbench_review(
    testbench_code: str
) -> dict:

    prompt = f"""
You are an expert hardware verification engineer
specialized in Python and cocotb.

Review the following cocotb testbench for a 2-to-4 decoder.

Check for:

1. Python syntax errors
2. Incorrect cocotb usage
3. Incorrect DUT signal names
4. Incorrect expected values
5. Missing input combinations
6. Incorrect assertions
7. Timing issues
8. Insufficient test coverage
9. Potential simulation failures

The 2-to-4 decoder should behave as:

00 -> 0001
01 -> 0010
10 -> 0100
11 -> 1000

Return ONLY valid JSON.

Use exactly this format:

{{
    "status": "PASS or FAIL",
    "details": "Short explanation",
    "issues": [
        "Issue 1",
        "Issue 2"
    ]
}}

If no issues exist:

{{
    "status": "PASS",
    "details": "Testbench correctly tests all decoder inputs.",
    "issues": []
}}

Cocotb testbench:

{testbench_code}
"""

    try:

        response = client.responses.create(
            model="gpt-5",
            input=prompt
        )

        result = parse_ai_json(
            response.output_text
        )

        return {
            "stage": "Testbench Review",
            "status": result.get(
                "status",
                "FAIL"
            ),
            "details": result.get(
                "details",
                ""
            ),
            "issues": result.get(
                "issues",
                []
            )
        }

    except Exception as e:

        return {
            "stage": "Testbench Review",
            "status": "FAIL",
            "details": f"AI review failed: {str(e)}",
            "issues": []
        }


# ============================================================
# SIMULATION VALIDATION
# ============================================================

def validate_simulation_results(
    sim_output: str,
    return_code: int
) -> dict:

    try:

        if not os.path.exists(
            RESULTS_PATH
        ):

            return {
                "stage": "Simulation Validation",
                "status": "FAIL",
                "details": (
                    "results.xml was not generated. "
                    "Simulation may have failed.\n\n"
                    f"Return code: {return_code}\n\n"
                    f"Output:\n{sim_output[-2000:]}"
                )
            }

        tree = ET.parse(
            RESULTS_PATH
        )

        root = tree.getroot()

        if root.tag == "testsuite":

            suites = [root]

        else:

            suites = root.findall(
                ".//testsuite"
            )

        failures = sum(
            int(
                suite.get(
                    "failures",
                    0
                )
            )
            for suite in suites
        )

        errors = sum(
            int(
                suite.get(
                    "errors",
                    0
                )
            )
            for suite in suites
        )

        tests = sum(
            int(
                suite.get(
                    "tests",
                    0
                )
            )
            for suite in suites
        )

        if (
            failures > 0
            or errors > 0
            or return_code != 0
        ):

            return {
                "stage": "Simulation Validation",
                "status": "FAIL",
                "details": (
                    f"Tests: {tests}, "
                    f"Failures: {failures}, "
                    f"Errors: {errors}"
                )
            }

        return {
            "stage": "Simulation Validation",
            "status": "PASS",
            "details": (
                f"All {tests} simulation test(s) "
                f"passed successfully."
            )
        }

    except Exception as e:

        return {
            "stage": "Simulation Validation",
            "status": "FAIL",
            "details": (
                f"Could not validate simulation: "
                f"{str(e)}"
            )
        }


# ============================================================
# RUN SIMULATION
# ============================================================

def run_simulation() -> dict:

    # Remove old results.xml
    if os.path.exists(
        RESULTS_PATH
    ):
        os.remove(
            RESULTS_PATH
        )

    try:

        result = subprocess.run(
            ["make", "run"],
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR,
            timeout=120
        )

        sim_output = (
            result.stdout
            + "\n"
            + result.stderr
        )

        return validate_simulation_results(
            sim_output,
            result.returncode
        )

    except subprocess.TimeoutExpired:

        return {
            "stage": "Simulation Validation",
            "status": "FAIL",
            "details": (
                "Simulation timed out "
                "after 120 seconds."
            )
        }

    except Exception as e:

        return {
            "stage": "Simulation Validation",
            "status": "FAIL",
            "details": (
                f"Simulation execution failed: "
                f"{str(e)}"
            )
        }


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline(
    design_code: str,
    testbench_code: str
) -> dict:

    # Step 1: AI reviews the RTL
    design_review = ai_design_review(
        design_code
    )

    # Step 2: AI reviews the testbench
    testbench_review = ai_testbench_review(
        testbench_code
    )

    # Step 3: Run actual simulation
    #
    # We run simulation even if AI finds issues,
    # because the simulator provides the real result.

    simulation_validation = run_simulation()

    return {
        "design_review": design_review,
        "testbench_review": testbench_review,
        "simulation_validation": (
            simulation_validation
        )
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
# API VALIDATE
# ============================================================

@app.route(
    "/validate",
    methods=["POST"]
)
def validate():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "status": "FAIL",
                "error": "No JSON data received"
            }), 400

        design_code = data.get(
            "design",
            ""
        )

        testbench_code = data.get(
            "testbench",
            ""
        )

        if not design_code:

            return jsonify({
                "status": "FAIL",
                "error": "Design code is empty"
            }), 400

        if not testbench_code:

            return jsonify({
                "status": "FAIL",
                "error": "Testbench code is empty"
            }), 400

        result = run_pipeline(
            design_code,
            testbench_code
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "status": "FAIL",
            "error": str(e)
        }), 500


# ============================================================
# RUN DECODER
# ============================================================

@app.route(
    "/run_decoder",
    methods=["POST"]
)
def run_decoder():

    try:

        with open(
            DESIGN_PATH,
            "r"
        ) as file:

            design_code = file.read()

        with open(
            TESTBENCH_PATH,
            "r"
        ) as file:

            testbench_code = file.read()

        result = run_pipeline(
            design_code,
            testbench_code
        )

        return jsonify(result)

    except FileNotFoundError as e:

        return jsonify({
            "status": "FAIL",
            "error": f"File not found: {str(e)}"
        }), 404

    except Exception as e:

        return jsonify({
            "status": "FAIL",
            "error": str(e)
        }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )