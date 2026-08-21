from flask import Flask, jsonify
from vcdvcd import VCDVCD

app = Flask(__name__)

VCD_FILE = "4bit_adder.vcd"


@app.route("/full_adder")
def full_adder():

    vcd = VCDVCD(VCD_FILE)

    signals = {}

    for signal in vcd.signals:
        signals[signal] = vcd[signal].tv

    return jsonify({
        "module": "full_adder",
        "signals": signals
    })


app.run(debug=True)
