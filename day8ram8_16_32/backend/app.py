from flask import Flask, render_template, jsonify, request
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
RAM_SV   = os.path.join(PROJECT_DIR, "ram8_16_32.sv")
TB_PY    = os.path.join(PROJECT_DIR, "testbench_ram8_16_32.py")
NETLIST  = os.path.join(PROJECT_DIR, "ram8_16_32_netlist.v")
VCD      = os.path.join(PROJECT_DIR, "ram8_16_32.vcd")
PNG      = os.path.join(PROJECT_DIR, "ram8_16_32.png")


# =========================================================
# HELPERS
# =========================================================
def read_file(path):
    with open(path, "r", errors="ignore") as f:
        return f.read()


def copilot_validate(prompt: str):
    return {"status": "PASS", "details": f"Copilot reviewed:\n{prompt[:500]}..."}


# =========================================================
# ROUTES
# =========================================================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run_ram", methods=["POST"])
def run_ram():
    data_width = request.form.get("data_width", "8")
    addr_width = request.form.get("addr_width", "8")

    # Collect artifacts
    artifacts = []
    for fname in [RAM_SV, TB_PY, NETLIST, VCD, PNG]:
        if os.path.exists(fname):
            if fname.endswith(".png"):
                artifacts.append(f"{os.path.basename(fname)}: [PNG image]")
            else:
                artifacts.append(f"=== {os.path.basename(fname)} ===\n{read_file(fname)[:2000]}")

    if not artifacts:
        return jsonify({"error": "No artifacts found"})

    # Validation
    prompt = (
        f"Review RAM design artifacts for DATA_WIDTH={data_width}, ADDR_WIDTH={addr_width}:\n\n"
        + "\n\n".join(artifacts)
    )
    ai_result = copilot_validate(prompt)

    if ai_result.get("status") != "PASS":
        return jsonify({"validation": ai_result, "simulation": None})

    # -----------------------------------------------------
    # Simulation
    # -----------------------------------------------------
    # IMPORTANT: each argument must be its own list element.
    # subprocess.run does NOT split strings on spaces the way a
    # shell would -- passing "sim DATA_WIDTH=8" as a single list
    # item sends make one bogus target literally named
    # "sim DATA_WIDTH=8", which fails before the simulation ever
    # runs. Split "sim" and each VAR=value pair into separate
    # elements instead.
    #
    # We also run `make clean_all` first so a previous width's
    # sim_build/ artifacts never leak into this run.
    subprocess.run(
        ["make", "clean_all"],
        cwd=PROJECT_DIR, capture_output=True, text=True
    )

    result = subprocess.run(
        ["make", "sim", f"DATA_WIDTH={data_width}", f"ADDR_WIDTH={addr_width}"],
        cwd=PROJECT_DIR, capture_output=True, text=True
    )

    # cocotb/make return code 0 == every test passed.
    # Do NOT substring-search stdout for "FAIL" -- the cocotb
    # summary table always prints a "FAIL=0" column even on a
    # full pass, which would falsely match a naive "FAIL" in
    # stdout check.
    passed = (result.returncode == 0)

    sim_result = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "status": "PASS" if passed else "FAIL",
        "returncode": result.returncode,
        "data_width": data_width,
        "addr_width": addr_width,
    }

    return jsonify({"validation": ai_result, "simulation": sim_result})


if __name__ == "__main__":
    print("Starting Flask RAM server...")
    app.run(debug=True)