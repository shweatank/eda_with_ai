from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
import subprocess

app = Flask(__name__)


# Project root directory
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent


@app.route("/")
def home():
    return send_from_directory(
        BASE_DIR / "static",
        "index.html"
    )


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/operations")
def get_operations():

    return jsonify({
        "operations": [
            "add_unsigned",
            "add_signed",
            "sub_unsigned",
            "sub_signed",
            "mul_unsigned",
            "mul_signed",
            "div_unsigned",
            "div_signed"
        ]
    })


@app.route("/alu/calculate", methods=["POST"])
def calculate_alu():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Invalid JSON data"
        }), 400


    operation = data.get("operation")
    a = data.get("a")
    b = data.get("b")


    if operation is None or a is None or b is None:
        return jsonify({
            "error": "operation, a and b are required"
        }), 400


    try:
        a = int(a)
        b = int(b)

    except ValueError:
        return jsonify({
            "error": "A and B must be integers"
        }), 400


    valid_operations = [
        "add_unsigned",
        "add_signed",
        "sub_unsigned",
        "sub_signed",
        "mul_unsigned",
        "mul_signed",
        "div_unsigned",
        "div_signed"
    ]


    if operation not in valid_operations:
        return jsonify({
            "error": "Invalid operation"
        }), 400


    # Unsigned validation
    if operation.endswith("unsigned"):

        if not (0 <= a <= 255 and 0 <= b <= 255):

            return jsonify({
                "error": "Unsigned values must be between 0 and 255"
            }), 400


    # Signed validation
    if operation.endswith("signed"):

        if not (-128 <= a <= 127 and -128 <= b <= 127):

            return jsonify({
                "error": "Signed values must be between -128 and 127"
            }), 400


    # ---------------- Addition ----------------

    if operation == "add_unsigned":

        result = (a + b) % 256


    elif operation == "add_signed":

        result = ((a + b + 128) % 256) - 128


    # ---------------- Subtraction ----------------

    elif operation == "sub_unsigned":

        result = (a - b) % 256


    elif operation == "sub_signed":

        result = ((a - b + 128) % 256) - 128


    # ---------------- Multiplication ----------------

    elif operation == "mul_unsigned":

        result = a * b


    elif operation == "mul_signed":

        result = a * b


    # ---------------- Division ----------------

    elif operation == "div_unsigned":

        if b == 0:

            result = {
                "quotient": 0,
                "remainder": 0
            }

        else:

            result = {
                "quotient": a // b,
                "remainder": a % b
            }


    elif operation == "div_signed":

        if b == 0:

            result = {
                "quotient": 0,
                "remainder": 0
            }

        else:

            # Verilog-style truncation toward zero
            quotient = abs(a) // abs(b)

            if (a < 0) ^ (b < 0):
                quotient = -quotient

            remainder = a - quotient * b

            result = {
                "quotient": quotient,
                "remainder": remainder
            }


    return jsonify({
        "operation": operation,
        "a": a,
        "b": b,
        "result": result
    })


@app.route("/simulate", methods=["POST"])
def run_simulation():

    data = request.get_json()

    operation = data.get("operation")

    valid_operations = [
        "add_unsigned",
        "add_signed",
        "sub_unsigned",
        "sub_signed",
        "mul_unsigned",
        "mul_signed",
        "div_unsigned",
        "div_signed",
        "top"
    ]


    if operation not in valid_operations:

        return jsonify({
            "error": "Invalid operation"
        }), 400


    try:

        result = subprocess.run(
            ["make", operation],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120
        )


        return jsonify({
            "operation": operation,
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        })


    except subprocess.TimeoutExpired:

        return jsonify({
            "error": "Simulation timed out"
        }), 408


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )