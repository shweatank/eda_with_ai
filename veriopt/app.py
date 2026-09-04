from flask import Flask, request, jsonify, render_template, send_from_directory
from graphql import build_schema, graphql_sync
import subprocess, os, re, glob, shutil

app = Flask(__name__, template_folder="templates")

schema = build_schema("""
    type Design {
        id: ID!
        name: String!
        filePath: String!
        status: String!
        report: String
    }

    type Query {
        hello: String
    }

    type Mutation {
        generateDesign(name: String!): Design
        generateTestbench(name: String!, tbType: String!): Design
        simulate: Design
        synthesize: Design
        waveform: Design
        schematic: Design
        placeAndRoute: Design
        staticTimingAnalysis: Design
        physicalSignoff: Design
    }
""")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# GTK/XDG env vars that VS Code's Snap packaging leaks into its integrated
# terminal, which cause gtkwave to load mismatched Snap-bundled GTK modules
# and crash with a symbol lookup error. Cleared before every gtkwave launch,
# mirroring the same fix applied to the Makefile's `wave` target.
GTKWAVE_CLEAN_ENV_VARS = (
    "GTK_EXE_PREFIX", "GTK_PATH", "GIO_MODULE_DIR", "GTK_IM_MODULE_FILE",
    "GDK_PIXBUF_MODULE_FILE", "XDG_DATA_DIRS", "XDG_DATA_HOME",
    "GSETTINGS_SCHEMA_DIR", "LOCPATH",
)


def clean_gtkwave_env():
    """Return a copy of the current environment with the Snap/VS-Code GTK
    variables removed, safe to pass to a gtkwave subprocess."""
    env = os.environ.copy()
    for var in GTKWAVE_CLEAN_ENV_VARS:
        env.pop(var, None)
    return env


def clean_name(name):
    """Restrict module/design names to safe identifier characters.

    This is used both as a filesystem-safe name and is interpolated into
    shell commands elsewhere, so it must not allow spaces, slashes, quotes,
    semicolons, etc.
    """
    if not NAME_RE.match(name):
        raise ValueError(
            "Invalid name: only letters, digits, and underscores are allowed, "
            "and the name must start with a letter or underscore."
        )
    return name


def safe_filename(name, ext):
    return f"{name.lower()}{ext}"


def last_error_lines(exc, n=5):
    """Return the last `n` non-empty lines of a failed subprocess's output.

    `make` always appends its own generic banner as the final line of
    stderr, e.g. "make: *** [Makefile:73: synth] Error 1". That line alone
    is never useful. The actual cause (missing tool, verilator lint
    failure, Yosys error, etc.) is printed on the line(s) before it, so we
    keep a short tail of output instead of just the last line.
    """
    combined = "\n".join(part for part in (exc.stdout, exc.stderr) if part)
    lines = [line for line in combined.strip().splitlines() if line.strip()]
    if not lines:
        return str(exc)
    return " | ".join(lines[-n:])


def generate_code(prompt, filepath):
    try:
        result = subprocess.run(
            ["ollama", "run", "llama2:7b", prompt],
            capture_output=True, text=True, check=True
        )
        code = result.stdout

        # Extract only code inside triple backticks
        match = re.search(r"```(?:systemverilog|verilog|python)?\n(.*?)```", code, re.DOTALL)
        if match:
            code = match.group(1)

        # Remove comments and explanatory lines
        code = "\n".join(line for line in code.splitlines()
                         if not line.strip().startswith("//")
                         and not line.strip().startswith("#")
                         and not line.lower().startswith("here is")
                         and not line.lower().startswith("note"))

        # Ensure file starts at 'module'
        lines = code.splitlines()
        for i, line in enumerate(lines):
            if line.strip().startswith("module"):
                code = "\n".join(lines[i:])
                break

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(code)
        return filepath
    except Exception as e:
        return f"Error generating code: {e}"


def ensure_dump_block(filepath, module_name):
    """Guarantee a $dumpfile/$dumpvars block exists in the generated file,
    regardless of whether the LLM actually included one.

    Small local models frequently drop trailing boilerplate once they've
    generated the "main" logic, so this is enforced deterministically in
    code rather than relied upon from the prompt alone.
    """
    with open(filepath, "r") as f:
        content = f.read()

    if "$dumpfile" in content:
        return  # already present

    dump_block = (
        f'\ninitial begin\n'
        f'    $dumpfile("{module_name}.vcd");\n'
        f'    $dumpvars(0, {module_name});\n'
        f'end\n'
    )

    idx = content.rfind("endmodule")
    if idx == -1:
        content += dump_block + "\nendmodule\n"
    else:
        content = content[:idx] + dump_block + content[idx:]

    with open(filepath, "w") as f:
        f.write(content)


# Matches a single always block sensitive to both a clock and a reset edge,
# e.g.  always @(posedge clk or posedge rst) begin ... end
_DUAL_EDGE_ALWAYS_RE = re.compile(
    r"always\s*@\s*\(\s*posedge\s+(\w+)\s+or\s+posedge\s+(\w+)\s*\)\s*begin"
    r"(?P<body>.*?)"
    r"\nend",
    re.IGNORECASE | re.DOTALL,
)


def ensure_valid_reset_pattern(filepath, output_signal="data_out", data_signal="data_in"):
    """Detect and repair the exact bug class that trips Yosys with
    'Multiple edge sensitive events found for this signal'.

    Small local models frequently generate a clock+reset sensitive always
    block but then forget the `if (rst) ... else ...` branch inside it,
    leaving an unconditional assignment that Yosys can't map to a single
    flip-flop. If that pattern is detected, rewrite the block deterministically
    with a proper async-reset structure instead of failing at synth time.
    """
    with open(filepath, "r") as f:
        content = f.read()

    match = _DUAL_EDGE_ALWAYS_RE.search(content)
    if not match:
        return  # no dual-edge always block found; nothing to check

    clk_signal, rst_signal = match.group(1), match.group(2)
    body = match.group("body")

    # If the body already branches on the reset signal, assume it's fine.
    if re.search(rf"\bif\s*\(\s*{re.escape(rst_signal)}\s*\)", body):
        return

    fixed_block = (
        f"always @(posedge {clk_signal} or posedge {rst_signal}) begin\n"
        f"    if ({rst_signal}) begin\n"
        f"        {output_signal} <= 1'b0;\n"
        f"    end else begin\n"
        f"        {output_signal} <= {data_signal};\n"
        f"    end\n"
        f"end"
    )

    content = content[:match.start()] + fixed_block + content[match.end():]

    with open(filepath, "w") as f:
        f.write(content)


def generate_design_deterministic(name, output_dir="src"):
    """Write the fixed-structure design file directly instead of asking an
    LLM to reproduce it.

    resolve_generate_design's prompt already specifies the entire module
    body verbatim -- only the module name actually varies. Since the
    structure is fully known ahead of time, having a small local model
    retype it introduces failure modes (dropped `if (rst)` branches,
    dropped dump blocks, extra commentary) with zero upside: there is no
    creative content here for the LLM to add. Generating it directly in
    Python guarantees a synthesizable file on every call.
    """
    filepath = os.path.join(output_dir, safe_filename(name, ".sv"))
    content = (
        "`timescale 1ns/1ps\n\n"
        f"module {name} (\n"
        "    input clk,\n"
        "    input rst,\n"
        "    input data_in,\n"
        "    output reg data_out\n"
        ");\n\n"
        "always @(posedge clk or posedge rst) begin\n"
        "    if (rst) begin\n"
        "        data_out <= 1'b0;\n"
        "    end else begin\n"
        "        data_out <= data_in;\n"
        "    end\n"
        "end\n\n"
        "initial begin\n"
        f'    $dumpfile("{name}.vcd");\n'
        f"    $dumpvars(0, {name});\n"
        "end\n\n"
        "endmodule\n"
    )
    os.makedirs(output_dir, exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content)
    return filepath


def generate_sv_testbench_deterministic(name, output_dir="tb"):
    """Write a working SystemVerilog testbench for the fixed design template
    (ports: clk, rst, data_in, data_out) directly, instead of asking an LLM
    to invent one.

    Drives a clock, applies reset, toggles data_in, and calls $finish so the
    simulation actually terminates and the design's own $dumpvars block gets
    flushed to a .vcd file.
    """
    filepath = os.path.join(output_dir, safe_filename(f"test_{name}", ".sv"))
    content = (
        "`timescale 1ns/1ps\n\n"
        f"module test_{name};\n\n"
        "    reg clk;\n"
        "    reg rst;\n"
        "    reg data_in;\n"
        "    wire data_out;\n\n"
        f"    {name} dut (\n"
        "        .clk(clk),\n"
        "        .rst(rst),\n"
        "        .data_in(data_in),\n"
        "        .data_out(data_out)\n"
        "    );\n\n"
        "    // 10ns period clock\n"
        "    initial clk = 1'b0;\n"
        "    always #5 clk = ~clk;\n\n"
        "    initial begin\n"
        "        rst = 1'b1;\n"
        "        data_in = 1'b0;\n\n"
        "        @(posedge clk);\n"
        "        @(posedge clk);\n"
        "        rst = 1'b0;\n\n"
        "        @(posedge clk);\n"
        "        data_in = 1'b1;\n"
        "        @(posedge clk);\n"
        "        data_in = 1'b0;\n"
        "        @(posedge clk);\n"
        "        data_in = 1'b1;\n\n"
        "        repeat (5) @(posedge clk);\n\n"
        "        $finish;\n"
        "    end\n\n"
        "endmodule\n"
    )
    os.makedirs(output_dir, exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content)
    return filepath


def generate_cocotb_testbench_deterministic(name, output_dir="tb"):
    """Write a working cocotb testbench for the fixed design template
    directly, instead of asking an LLM to invent one.

    Uses only real cocotb APIs: cocotb.clock.Clock, cocotb.triggers.RisingEdge,
    and cocotb.triggers.Timer with proper units -- avoiding the class of bugs
    where a local model hallucinates nonexistent APIs (e.g. cocotb.TestObject)
    or assigns incompatible types to single-bit signals.
    """
    filepath = os.path.join(output_dir, safe_filename(f"test_{name}", ".py"))
    content = (
        "import cocotb\n"
        "from cocotb.clock import Clock\n"
        "from cocotb.triggers import RisingEdge, Timer\n\n\n"
        "@cocotb.test()\n"
        f"async def test_{name}_reset(dut):\n"
        "    clock = Clock(dut.clk, 10, unit=\"ns\")\n"
        "    cocotb.start_soon(clock.start())\n\n"
        "    dut.rst.value = 1\n"
        "    dut.data_in.value = 0\n"
        "    await RisingEdge(dut.clk)\n"
        "    await RisingEdge(dut.clk)\n\n"
        "    assert dut.data_out.value == 0, \"data_out should be 0 during reset\"\n\n"
        "    dut.rst.value = 0\n"
        "    await RisingEdge(dut.clk)\n\n\n"
        "@cocotb.test()\n"
        f"async def test_{name}_data_passthrough(dut):\n"
        "    clock = Clock(dut.clk, 10, unit=\"ns\")\n"
        "    cocotb.start_soon(clock.start())\n\n"
        "    dut.rst.value = 1\n"
        "    dut.data_in.value = 0\n"
        "    await RisingEdge(dut.clk)\n"
        "    dut.rst.value = 0\n"
        "    await RisingEdge(dut.clk)\n\n"
        "    dut.data_in.value = 1\n"
        "    await RisingEdge(dut.clk)\n"
        "    await Timer(1, unit=\"ns\")\n"
        "    assert dut.data_out.value == 1, \"data_out should follow data_in\"\n\n"
        "    dut.data_in.value = 0\n"
        "    await RisingEdge(dut.clk)\n"
        "    await Timer(1, unit=\"ns\")\n"
        "    assert dut.data_out.value == 0, \"data_out should follow data_in\"\n"
    )
    os.makedirs(output_dir, exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content)
    return filepath

def resolve_hello(obj, info):
    return "GraphQL backend is alive!"


def resolve_generate_design(obj, info, name):
    try:
        name = clean_name(name)
    except ValueError as e:
        return {"id": "1", "name": name, "filePath": "", "status": f"error: {e}"}

    # No LLM call: the module structure is fully fixed (only the name
    # varies), so it's generated deterministically -- always synthesizable,
    # never dependent on how well the local model follows instructions.
    filepath = generate_design_deterministic(name)

    return {"id": "1", "name": name, "filePath": filepath, "status": "rtl_generated"}


def resolve_generate_testbench(obj, info, name, tbType):
    try:
        name = clean_name(name)
    except ValueError as e:
        return {"id": "2", "name": name, "filePath": "", "status": f"error: {e}"}

    # No LLM call: same rationale as resolve_generate_design -- the DUT's
    # port list (clk, rst, data_in, data_out) is fixed, so the testbench
    # structure is fully determined. Writing it directly avoids the LLM
    # inventing nonexistent APIs (e.g. cocotb.TestObject) or forgetting
    # $finish / the clock-toggle loop, both of which silently prevent any
    # .vcd file from ever being produced.
    if tbType.lower() == "python":
        filepath = generate_cocotb_testbench_deterministic(name)
    else:
        filepath = generate_sv_testbench_deterministic(name)

    return {"id": "2", "name": f"{name}_tb", "filePath": filepath, "status": "tb_generated"}


def resolve_simulate(obj, info):
    try:
        # Pick the sim target based on which testbench flavor exists for the
        # most recently generated design.
        sv_tbs = glob.glob(os.path.join("tb", "test_*.sv"))
        py_tbs = glob.glob(os.path.join("tb", "test_*.py"))
        target = "sim-cocotb" if (py_tbs and not sv_tbs) else "sim"

        result = subprocess.run(
            ["make", target], capture_output=True, text=True, check=True
        )

        # Pick up whichever .vcd file the testbench actually produced,
        # instead of assuming a fixed name like "uart.vcd".
        vcd_files = glob.glob("*.vcd")
        os.makedirs("results", exist_ok=True)
        if vcd_files:
            latest_vcd = max(vcd_files, key=os.path.getmtime)
            os.rename(latest_vcd, "results/design.vcd")

        if not os.path.exists("results/design.vcd"):
            return {"id": "3", "name": "latest_design", "filePath": "results/design.vcd",
                    "status": "simulation_failed: no .vcd file was produced"}

        # Waveform PNG generation is best-effort and optional: a broken or
        # missing gtkwave install (a system dependency, unrelated to the
        # simulation itself) should not turn a successful simulation into a
        # reported failure. The .vcd is the actual deliverable of this step.
        try:
            subprocess.run(["make", "wave"], capture_output=True, text=True, check=True)
            status = "simulated_with_waveform"
        except subprocess.CalledProcessError as wave_err:
            wave_detail = last_error_lines(wave_err)
            status = f"simulated_no_waveform_png: {wave_detail}"

        return {"id": "3", "name": "latest_design", "filePath": "results/design.vcd", "status": status}
    except subprocess.CalledProcessError as e:
        detail = last_error_lines(e)
        return {"id": "3", "name": "latest_design", "filePath": "results/design.vcd", "status": f"simulation_failed: {detail}"}


def resolve_synthesize(obj, info):
    """Delegate to `make synth`, which strips the simulation-only dump block,
    runs verilator lint as a hard gate, then runs Yosys. Keeping this logic
    in the Makefile (rather than duplicated in Python) means `make synth`
    run by hand and synthesis triggered via GraphQL always behave the same.
    """
    try:
        design_files = [f for f in os.listdir("src") if f.endswith(".sv")]
        if not design_files:
            return {"id": "4", "name": "latest_design", "filePath": "", "status": "synthesis_failed: No RTL design found"}

        os.makedirs("results", exist_ok=True)
        subprocess.run(["make", "synth"], capture_output=True, text=True, check=True)
        return {"id": "4", "name": "latest_design", "filePath": "results/netlist.v", "status": "synthesized"}
    except subprocess.CalledProcessError as e:
        # Surface make's actual stderr/stdout (verilator lint error or Yosys
        # error) instead of just the exit code.
        detail = last_error_lines(e)
        return {"id": "4", "name": "latest_design", "filePath": "results/netlist.v", "status": f"synthesis_failed: {detail}"}


def resolve_waveform(obj, info):
    vcd_path = "results/design.vcd"
    png_path = "results/design.png"
    if not os.path.exists(vcd_path):
        return {"id": "5", "name": "waveform", "filePath": "", "status": "waveform_failed: No VCD file found"}
    try:
        subprocess.run(["make", "wave"], capture_output=True, text=True, check=True)
        return {"id": "5", "name": "waveform", "filePath": png_path, "status": "waveform_generated"}
    except subprocess.CalledProcessError as e:
        detail = last_error_lines(e)
        return {"id": "5", "name": "waveform", "filePath": "", "status": f"waveform_failed: {detail}"}


def resolve_schematic(obj, info):
    """Render an RTL schematic PNG via `make schematic` (Yosys `show` ->
    Graphviz `dot`), separate from the waveform PNG: this shows circuit
    structure, not signal traces over time.
    """
    try:
        design_files = [f for f in os.listdir("src") if f.endswith(".sv")]
        if not design_files:
            return {"id": "6", "name": "schematic", "filePath": "", "status": "schematic_failed: No RTL design found"}

        os.makedirs("results", exist_ok=True)
        subprocess.run(["make", "schematic"], capture_output=True, text=True, check=True)

        design_name = os.path.splitext(sorted(
            design_files, key=lambda f: os.path.getmtime(os.path.join("src", f))
        )[-1])[0]
        png_path = f"results/{design_name}.png"

        return {"id": "6", "name": "schematic", "filePath": png_path, "status": "schematic_generated"}
    except subprocess.CalledProcessError as e:
        detail = last_error_lines(e)
        return {"id": "6", "name": "schematic", "filePath": "", "status": f"schematic_failed: {detail}"}


# ---------------------------------------------------------------------------
# Physical implementation: place and route, signoff timing, signoff checks
#
# Each of these shells out to the corresponding Makefile target, so the flow
# behaves identically whether it is driven from this dashboard or from the
# command line. They are slow by nature -- a full place and route walks
# floorplan, PDN, placement, CTS and routing -- so each carries an explicit
# timeout rather than letting a wedged tool hold the request open forever.
# ---------------------------------------------------------------------------

PNR_DIR = os.path.join("results", "pnr")

# Generous enough for a real block, short enough that a hung tool eventually
# releases the request. Place and route is the long pole by a wide margin.
STAGE_TIMEOUTS = {"pnr": 3600, "sta": 900, "signoff": 900}


def current_design_name():
    """Name of the design the Makefile would pick: newest .sv under src/.

    Mirrors the Makefile's `ls -t src/*.sv | head -n1`, so the report file the
    dashboard reads back is the one the stage just wrote.
    """
    designs = glob.glob(os.path.join("src", "*.sv"))
    if not designs:
        return None
    newest = max(designs, key=os.path.getmtime)
    return os.path.splitext(os.path.basename(newest))[0]


def read_summary(path):
    """Return the contents of a stage summary, or None if it wasn't written."""
    if not os.path.exists(path):
        return None
    with open(path, errors="replace") as handle:
        return handle.read()


def run_backend_stage(stage, target, summary_suffix, result_path, resolver_id):
    """Run one physical-implementation Makefile target and return its summary.

    The summary file is read back even when make exits non-zero: a stage can
    fail late (say the layout render) after the reports it produced are
    already valid and worth showing.
    """
    design = current_design_name()
    if design is None:
        return {"id": resolver_id, "name": "physical", "filePath": "", "report": None,
                "status": f"{stage}_failed: No RTL design found in src/"}

    summary_path = os.path.join(PNR_DIR, f"{design}{summary_suffix}")
    try:
        subprocess.run(["make", target], capture_output=True, text=True,
                       check=True, timeout=STAGE_TIMEOUTS[stage])
        status = f"{stage}_complete"
    except subprocess.TimeoutExpired:
        return {"id": resolver_id, "name": design, "filePath": "", "report": None,
                "status": f"{stage}_failed: timed out after {STAGE_TIMEOUTS[stage]}s"}
    except subprocess.CalledProcessError as e:
        status = f"{stage}_failed: {last_error_lines(e)}"

    return {
        "id": resolver_id,
        "name": design,
        "filePath": result_path.format(design=design),
        "status": status,
        "report": read_summary(summary_path),
    }


def resolve_place_and_route(obj, info):
    """Map to the PDK's standard cells and run OpenROAD place and route.

    `make pnr` covers the whole physical flow: technology mapping, floorplan,
    pin placement, tapcells, power grid, placement, clock tree synthesis,
    global and detailed routing, antenna repair, fillers, parasitic
    extraction, and a rendered layout PNG.
    """
    return run_backend_stage(
        "pnr", "pnr", "_summary.txt",
        os.path.join(PNR_DIR, "{design}_routed.def"), "7")


def resolve_sta(obj, info):
    """Post-route signoff timing under standalone OpenSTA.

    Reads the routed netlist plus the extracted SPEF, so the delays come from
    measured parasitics rather than the estimates place and route optimizes
    against. Requires a completed `placeAndRoute`.
    """
    return run_backend_stage(
        "sta", "sta", "_sta_summary.txt",
        os.path.join(PNR_DIR, "{design}_sta.rpt"), "8")


def resolve_signoff(obj, info):
    """Physical signoff checks on the routed database.

    Placement legality, unrouted nets, routing DRC, antenna violations, power
    grid connectivity and the library's electrical limits. Requires a
    completed `placeAndRoute`.
    """
    return run_backend_stage(
        "signoff", "signoff", "_signoff_summary.txt",
        os.path.join(PNR_DIR, "{design}_signoff.rpt"), "9")

schema.get_type("Query").fields["hello"].resolve = resolve_hello
mutation = schema.get_type("Mutation").fields
mutation["generateDesign"].resolve = resolve_generate_design
mutation["generateTestbench"].resolve = resolve_generate_testbench
mutation["simulate"].resolve = resolve_simulate
mutation["synthesize"].resolve = resolve_synthesize
mutation["waveform"].resolve = resolve_waveform
mutation["schematic"].resolve = resolve_schematic
mutation["placeAndRoute"].resolve = resolve_place_and_route
mutation["staticTimingAnalysis"].resolve = resolve_sta
mutation["physicalSignoff"].resolve = resolve_signoff


@app.route("/", methods=["GET"])
def index():
    return "GraphQL backend is running. Visit /dashboard for UI"


@app.route("/graphql", methods=["POST"])
def graphql_server():
    payload = request.get_json() or {}
    result = graphql_sync(schema, payload.get("query"), variable_values=payload.get("variables"))
    response = {}
    if result.data is not None:
        response["data"] = result.data
    if result.errors:
        response["errors"] = [error.formatted for error in result.errors]
    return jsonify(response)


@app.route("/dashboard")
def dashboard():
    return render_template("index.html")


@app.route("/api/view-waveform", methods=["POST"])
def view_waveform():
    """Launch gtkwave as a live GUI window against the most recent VCD.

    This opens gtkwave on the machine running the Flask process (not in the
    browser) -- it's meant for local development use, same as running
    `gtkwave results/design.vcd` by hand, just triggered from the dashboard.
    """
    vcd_path = os.path.join("results", "design.vcd")

    if not os.path.exists(vcd_path):
        return jsonify({
            "status": "error",
            "message": "No VCD file found at results/design.vcd. Run Simulate first."
        }), 404

    if not shutil.which("gtkwave"):
        return jsonify({
            "status": "error",
            "message": "gtkwave not found. Install with: sudo apt-get install gtkwave"
        }), 500

    try:
        # Popen (not run): gtkwave is a GUI app that stays open, so we launch
        # it in the background instead of blocking the HTTP request on it.
        subprocess.Popen(
            ["gtkwave", vcd_path],
            env=clean_gtkwave_env(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return jsonify({"status": "ok", "message": f"Launched gtkwave for {vcd_path}"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to launch gtkwave: {e}"}), 500


@app.route("/results/<path:filename>")
def serve_result_file(filename):
    """Serve files from results/ so the dashboard can display generated
    PNGs (waveform or schematic) inline via a plain <img> tag.

    send_from_directory rejects any filename containing '..' or an absolute
    path on its own, so this can't be used to read files outside results/.
    """
    results_dir = os.path.abspath("results")
    return send_from_directory(results_dir, filename)


if __name__ == "__main__":
    app.run(debug=True)