from flask import Flask, jsonify
from vcd_reader import parse_vcd
import os

app = Flask(__name__)


@app.route("/")
def index():
    return app.send_static_file("andgate.html")

@app.route("/validate_vcd", methods=["GET"])
def validate_vcd():
    # Build absolute path to the VCD file
    file_path = os.path.abspath("/home/mirafra/vlsi/and_gate.vcd")

    # Check if file exists before parsing
    if not os.path.exists(file_path):
        return jsonify({"error": f"VCD file not found at {file_path}"}), 404

    data = parse_vcd(file_path)
    return jsonify(data)

@app.route("/signals", methods=["GET"])
def list_signals():
    file_path = os.path.abspath("/home/mirafra/vlsi/and_gate.vcd")
    data = parse_vcd(file_path)
    return jsonify([sig["name"] for sig in data.values()])

@app.route("/waveform/<signal>", methods=["GET"])
def get_waveform(signal):
    file_path = os.path.abspath("/home/mirafra/vlsi/and_gate.vcd")
    data = parse_vcd(file_path)
    for sig in data.values():
        if sig["name"] == signal:
            return jsonify(sig["values"])
    return jsonify({"error": "Signal not found"}), 404

@app.route("/check_and_gate", methods=["GET"])
def check_and_gate():
    file_path = os.path.abspath("/home/mirafra/vlsi/and_gate.vcd")
    data = parse_vcd(file_path)

    # Helper to safely fetch signal values by name
    def get_signal_values(name):
        for sig in data.values():
            if sig["name"] == name:
                return sig["values"]
        return None

    # Match your Cocotb testbench: signals are a, b, y
    a_vals = get_signal_values("a")
    b_vals = get_signal_values("b")
    out_vals = get_signal_values("y")  # Cocotb uses 'y' not 'out'

    if not all([a_vals, b_vals, out_vals]):
        missing = [n for n, v in zip(["a", "b", "y"], [a_vals, b_vals, out_vals]) if v is None]
        return jsonify({"error": f"Missing signals: {', '.join(missing)}"}), 404

    # Truth table check
    for t in range(len(out_vals)):
        expected = str(int(a_vals[t]["value"]) & int(b_vals[t]["value"]))
        if out_vals[t]["value"] != expected:
            return jsonify({"result": "FAIL", "time": out_vals[t]["time"]})
    return jsonify({"result": "PASS"})



if __name__ == "__main__":
    app.run(debug=True, port=5001)
