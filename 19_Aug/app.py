from flask import Flask, request, jsonify, render_template
import subprocess
import os

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/run", methods=["POST"])
def run_simulation():

    data = request.get_json()

    a = data.get("a")
    b = data.get("b")

    if a not in [0, 1] or b not in [0, 1]:
        return jsonify({
            "error": "a and b must be 0 or 1"
        }), 400

    env = os.environ.copy()
    env["INPUT_A"] = str(a)
    env["INPUT_B"] = str(b)

    result = subprocess.run(
        ["make"],
        capture_output=True,
        text=True,
        env=env
    )

    if result.returncode != 0:
        return jsonify({
            "status": "FAIL",
            "error": "RTL simulation failed"
        }), 500

    result_line = None

    for line in result.stdout.splitlines():
        if line.startswith("RESULT:"):
            result_line = line
            break

    if result_line is None:
        return jsonify({
            "status": "FAIL",
            "error": "Simulation result not found"
        }), 500

    values = result_line.replace("RESULT:", "").split(",")

    y = int(values[2])

    return jsonify({
        "status": "PASS",
        "a": a,
        "b": b,
        "y": y
    })


if __name__ == "__main__":
    app.run(debug=True)