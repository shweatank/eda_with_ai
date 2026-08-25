from flask import Flask, render_template, jsonify, request
import subprocess

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/simulate", methods=["POST"])
def simulate():
    try:
        # Run the default Makefile target (all)
        result = subprocess.run(["make"], capture_output=True, text=True)
        return jsonify({
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "status": result.returncode
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/ollama", methods=["POST"])
def ollama():
    query = request.json.get("q", "Explain RAM simulation")
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3", query],
            capture_output=True, text=True
        )
        return jsonify({"ollama_response": result.stdout.strip()})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
