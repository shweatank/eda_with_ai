from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, render_template, request
from test_arithmetic import run_arithmetic_simulation


app = Flask(__name__)

RTL_FILE = Path(__file__).with_name("arithmetic.sv")
OPERATIONS = {
    0: "sum",
    1: "subtract",
    2: "multiply",
    3: "divide",
    4: "remainder",
}


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_payload(payload: object) -> tuple[dict[str, int] | None, str | None]:
    if not isinstance(payload, dict):
        return None, "request body must be a JSON object"

    required_fields = ("a_u", "b_u", "a_s", "b_s", "op")
    missing_fields = [field for field in required_fields if field not in payload]
    if missing_fields:
        return None, f"missing fields: {', '.join(missing_fields)}"

    if any(not _is_integer(payload[field]) for field in required_fields):
        return None, "all fields must be integers"

    values = {field: int(payload[field]) for field in required_fields}
    ranges = {
        "a_u": (0, 255),
        "b_u": (0, 255),
        "a_s": (-128, 127),
        "b_s": (-128, 127),
        "op": (0, 4),
    }
    for field, (minimum, maximum) in ranges.items():
        if not minimum <= values[field] <= maximum:
            return None, f"{field} must be between {minimum} and {maximum}"

    return values, None


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/arithmetic")
@app.post("/run")
def run_arithmetic():
    values, error = _validate_payload(request.get_json(silent=True))
    if error:
        return jsonify({"status": "FAIL", "error": error}), 400

    try:
        unsigned_result, signed_result = run_arithmetic_simulation(values)
    except (OSError, RuntimeError, TimeoutError) as exc:
        return jsonify({"status": "FAIL", "error": str(exc)}), 500

    return jsonify(
        {
            "status": "PASS",
            **values,
            "operation": OPERATIONS[values["op"]],
            "u_result": unsigned_result,
            "s_result": signed_result,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)