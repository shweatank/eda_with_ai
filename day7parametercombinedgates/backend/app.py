from flask import Flask, render_template, jsonify
import subprocess, os

# =========================================================
# PROJECT ROOTS
# =========================================================
PROJECT_DIR   = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE_DIR  = os.path.join(PROJECT_DIR, "templates")
STATIC_DIR    = os.path.join(PROJECT_DIR, "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# =========================================================
# FILE PATHS
# =========================================================
COMBINED_SV   = os.path.join(PROJECT_DIR, "parameter_combinedgate.sv")
TB_PY         = os.path.join(PROJECT_DIR, "testbench_parameter_combinedgate.py")
NETLIST       = os.path.join(PROJECT_DIR, "vector_gates_combined_netlist.v")
VCD           = os.path.join(PROJECT_DIR, "vector_gates_combined.vcd")
PNG           = os.path.join(PROJECT_DIR, "vector_gates_combined.png")

# =========================================================
# HELPERS
# =========================================================
def read_file(path):
    with open(path, "r", errors="ignore") as f:
        return f.read()

def copilot_validate(prompt: str):
    """
    Stub for Copilot validation.
    Replace with actual Copilot API/SDK integration.
    """
    return {
        "status": "PASS",
        "details": f"Copilot reviewed:\n{prompt[:500]}..."
    }

# =========================================================
# ROUTES
# =========================================================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/simulate", methods=["POST"])
def simulate():
    result = subprocess.run(["make", "sim"], cwd=PROJECT_DIR,
                            capture_output=True, text=True)
    return jsonify({
        "stdout": result.stdout,
        "stderr": result.stderr,
        "status": result.returncode
    })

@app.route("/validate", methods=["POST"])
def validate():
    artifacts = []
    for fname in [COMBINED_SV, TB_PY, NETLIST, VCD, PNG]:
        if os.path.exists(fname):
            if fname.endswith(".png"):
                artifacts.append(f"{os.path.basename(fname)}: [PNG image]")
            else:
                artifacts.append(f"=== {os.path.basename(fname)} ===\n{read_file(fname)[:2000]}")
    if not artifacts:
        return jsonify({"error": "No artifacts found"})
    prompt = "Review these Vector Gates Combined design artifacts:\n\n" + "\n\n".join(artifacts)
    return jsonify(copilot_validate(prompt))

@app.route("/run_combined", methods=["POST"])
def run_combined():
    # Step 1: Collect artifacts
    artifacts = []
    for fname in [COMBINED_SV, TB_PY, NETLIST, VCD, PNG]:
        if os.path.exists(fname):
            if fname.endswith(".png"):
                artifacts.append(f"{os.path.basename(fname)}: [PNG image]")
            else:
                artifacts.append(f"=== {os.path.basename(fname)} ===\n{read_file(fname)[:2000]}")

    if not artifacts:
        return jsonify({"error": "No artifacts found"})

    # Step 2: AI validation
    prompt = "Review these Vector Gates Combined design artifacts:\n\n" + "\n\n".join(artifacts)
    ai_result = copilot_validate(prompt)

    if ai_result.get("status") != "PASS":
        return jsonify({"validation": ai_result, "simulation": None})

    # Step 3: Run simulation
    result = subprocess.run(["make", "sim"], cwd=PROJECT_DIR,
                            capture_output=True, text=True)

    sim_result = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "status": result.returncode
    }

    if result.returncode != 0:
        return jsonify({"validation": ai_result, "simulation": sim_result})

    # Step 4: Return both validation + simulation success
    return jsonify({
        "validation": ai_result,
        "simulation": sim_result
    })

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(debug=True)
