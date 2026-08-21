from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from test_decoder import run_decoder_simulation


app = Flask(__name__)


def _parse_input(payload: object) -> tuple[int | None, str | None]:
    if not isinstance(payload, dict):
        return None, "request body must be a JSON object"

    value = payload.get("a")
    if isinstance(value, bool) or not isinstance(value, int):
        return None, "a must be an integer"
    if not 0 <= value <= 3:
        return None, "a must be between 0 and 3"
    return value, None


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/decoder")
@app.post("/api/decoder")
@app.get("/run")
@app.post("/run")
def run_decoder():
    if request.method == "GET":
        raw_value = request.args.get("a")
        payload = {"a": int(raw_value)} if raw_value and raw_value.lstrip("-").isdigit() else {"a": raw_value}
    else:
        payload = request.get_json(silent=True)

    value, error = _parse_input(payload)
    if error:
        return jsonify({"status": "FAIL", "error": error}), 400

    try:
        result = run_decoder_simulation(value)
    except (OSError, RuntimeError, TimeoutError) as exc:
        return jsonify({"status": "FAIL", "error": str(exc)}), 500

    return jsonify(
        {
            "status": "PASS",
            "a": value,
            "y": result,
            "y_binary": f"{result:04b}",
        }
    )


if __name__ == "__main__":
    app.run(debug=True)