from flask import Flask, render_template, jsonify
import subprocess, os

# Project root (day7rom)
PROJECT_DIR   = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE_DIR  = os.path.join(PROJECT_DIR, "templates")
STATIC_DIR    = os.path.join(PROJECT_DIR, "static")

# Flask knows templates and static are at the root
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# =========================================================
# FILE PATHS
# =========================================================
ROM_SV   = os.path.join(PROJECT_DIR, "rom.sv")
TB_PY    = os.path.join(PROJECT_DIR, "testbench_rom.py")
NETLIST  = os.path.join(PROJECT_DIR, "rom_netlist.v")
VCD      = os.path.join(PROJECT_DIR, "rom.vcd")
PNG      = os.path.join(PROJECT_DIR, "rom.png")

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
    for fname in [ROM_SV, TB_PY, NETLIST, VCD, PNG]:
        if os.path.exists(fname):
            if fname.endswith(".png"):
                artifacts.append(f"{os.path.basename(fname)}: [PNG image]")
            else:
                artifacts.append(f"=== {os.path.basename(fname)} ===\n{read_file(fname)[:2000]}")
    if not artifacts:
        return jsonify({"error": "No artifacts found"})
    prompt = "Review these ROM design artifacts:\n\n" + "\n\n".join(artifacts)
    return jsonify(copilot_validate(prompt))

if __name__ == "__main__":
    app.run(debug=True)
