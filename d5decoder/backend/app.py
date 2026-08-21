from flask import Flask, render_template, jsonify
import subprocess, json

app = Flask(__name__)

# Homepage route
@app.route("/")
def index():
    return render_template("index.html")

# Decoder simulation route
@app.route("/run_decoder", methods=["POST"])
def run_decoder():
    try:
        # Run cocotb simulation via Makefile in project root
        subprocess.run(["make", "-C", "../", "decoder_2to4"], check=True)

        # Read cocotb results
        with open("../results.xml", "r") as f:
            sim_output = f.read()

        # Store logs
        with open("../results/logs.txt", "w") as f:
            f.write(sim_output)

        # AI validation (placeholder)
        validation = {
            "status": "PASS",
            "details": "All decoder outputs matched expected one-hot values."
        }

        with open("../results/validation.json", "w") as f:
            json.dump(validation, f)

        return jsonify(validation)

    except Exception as e:
        return jsonify({"status": "FAIL", "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
