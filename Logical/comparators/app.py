from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request

from flask import Flask, jsonify, render_template, request

from test_comparator import run_comparator_simulation


app = Flask(__name__)
RESULTS_FILE = Path(__file__).with_name("comparator_results.jsonl")


def _parse_input(payload: object) -> tuple[dict[str, int] | None, str | None]:
    if not isinstance(payload, dict):
        return None, "request body must be a JSON object"

    if "a" not in payload or "b" not in payload:
        return None, "a and b are required"

    if any(isinstance(payload[name], bool) or not isinstance(payload[name], int) for name in ("a", "b")):
        return None, "a and b must be integers"

    values = {"a": payload["a"], "b": payload["b"]}
    for name, value in values.items():
        if not 0 <= value <= 255:
            return None, f"{name} must be between 0 and 255"
    return values, None


def _expected_outputs(a: int, b: int) -> dict[str, int]:
    return {
        "equal": int(a == b),
        "greater": int(a > b),
        "less": int(a < b),
    }


def _store_result(record: dict[str, object]) -> None:
    with RESULTS_FILE.open("a", encoding="utf-8") as result_file:
        result_file.write(json.dumps(record) + "\n")


def _local_analysis(record: dict[str, object]) -> dict[str, str]:
    expected = record["expected"]
    actual = record["rtl_output"]
    passed = expected == actual
    return {
        "source": "local-fallback",
        "verdict": "PASS" if passed else "FAIL",
        "message": "RTL outputs match the expected comparator behavior."
        if passed
        else "RTL outputs do not match the expected comparator behavior.",
    }


def _analyze_with_ai(record: dict[str, object]) -> dict[str, str]:
    """Send a stored RTL result to an optional OpenAI-compatible AI endpoint."""
    endpoint = os.getenv("AI_API_URL")
    api_key = os.getenv("AI_API_KEY")
    if not endpoint or not api_key:
        return _local_analysis(record)

    prompt = (
        "Analyze this comparator RTL result. Return JSON only with keys "
        "verdict (PASS or FAIL) and message. PASS only when rtl_output equals expected.\n"
        + json.dumps(record)
    )
    payload = {
        "model": os.getenv("AI_MODEL", "gpt-4o-mini"),
        "messages": [
            {"role": "system", "content": "You are an RTL verification assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
    }
    http_request = urllib_request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib_request.urlopen(http_request, timeout=15) as response:
            response_body = json.loads(response.read().decode("utf-8"))
        content = response_body["choices"][0]["message"]["content"]
        analysis = json.loads(content)
        verdict = analysis.get("verdict")
        message = analysis.get("message")
        if verdict not in {"PASS", "FAIL"} or not isinstance(message, str):
            raise ValueError("AI response must contain verdict and message")
        return {"source": "ai", "verdict": verdict, "message": message}
    except (OSError, ValueError, KeyError, IndexError, json.JSONDecodeError, urllib_error.URLError) as exc:
        fallback = _local_analysis(record)
        fallback["message"] += f" AI unavailable: {exc}"
        return fallback


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/comparator")
@app.post("/run")
def run_comparator():
    values, error = _parse_input(request.get_json(silent=True))
    if error:
        return jsonify({"status": "FAIL", "error": error}), 400

    try:
        equal, greater, less = run_comparator_simulation(values["a"], values["b"])
    except (OSError, RuntimeError, TimeoutError) as exc:
        return jsonify({"status": "FAIL", "error": str(exc)}), 500

    rtl_output = {"equal": equal, "greater": greater, "less": less}
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **values,
        "rtl_output": rtl_output,
        "expected": _expected_outputs(values["a"], values["b"]),
    }
    _store_result(record)
    ai_analysis = _analyze_with_ai(record)

    return jsonify({"status": "PASS", **values, **rtl_output, "ai_analysis": ai_analysis})


if __name__ == "__main__":
    app.run(debug=True)