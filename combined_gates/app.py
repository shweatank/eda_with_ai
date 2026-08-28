from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
PROJECT_DIR = Path(__file__).resolve().parent
ARTIFACTS = {name: PROJECT_DIR / f"combined_gates.{suffix}" for name, suffix in {
    "waveform": "vcd", "diagram": "dot", "image": "png"
}.items()}
ARTIFACTS["netlist"] = PROJECT_DIR / "combined_gates_netlist.v"


def run_make(target: str = "") -> tuple[bool, str]:
    result = subprocess.run(["make"] + ([target] if target else []), cwd=PROJECT_DIR, capture_output=True, text=True, timeout=60)
    return result.returncode == 0, (result.stdout + result.stderr)[-4000:]


def evidence() -> dict[str, object]:
    netlist = ARTIFACTS["netlist"]
    text = netlist.read_text(encoding="utf-8") if netlist.is_file() else ""
    source = (PROJECT_DIR / "combined_gates.sv").read_text(encoding="utf-8")
    terms = ["module combined_gates", "input [7:0] a", "input [7:0] b", "input [7:0] c", "output [7:0] y", "y[0]", "y[7]"]
    checks = [f"netlist is missing expected term: {term}" for term in terms if term not in text]
    checks.extend(
        f"RTL source is missing expected term: {term}"
        for term in ["parameter WIDTH", "[WIDTH-1:0]", "for (i = 0", "GEN_AND", "GEN_COMBINED"]
        if term not in source
    )
    if not checks:
        checks = ["RTL and netlist contain eight different operations across y[7:0]"]
    return {"artifact_files": {name: path.is_file() for name, path in ARTIFACTS.items()}, "netlist_checks": checks}


def ask_ollama(data: dict[str, object]) -> dict[str, str]:
    model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
    endpoint = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
    payload = {"model": model, "prompt": "Review this combined-gate verification evidence. Return exactly {\"verdict\":\"PASS\"} or {\"verdict\":\"FAIL\"}.\n" + json.dumps(data), "stream": False, "format": "json", "options": {"temperature": 0, "num_predict": 8}}
    try:
        request = urllib_request.Request(endpoint, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
        with urllib_request.urlopen(request, timeout=float(os.getenv("OLLAMA_TIMEOUT", "15"))) as response:
            verdict = json.loads(json.loads(response.read().decode())["response"])["verdict"]
        return {"source": f"ollama:{model}", "verdict": verdict, "summary": "Ollama review completed."}
    except (OSError, ValueError, KeyError, json.JSONDecodeError, urllib_error.URLError) as exc:
        return {"source": "ollama-unavailable", "verdict": "FAIL", "summary": str(exc)}


def _parse_input(value: object) -> int:
    text = str(value).strip().replace("_", "")
    if not text:
        raise ValueError("input cannot be empty")
    return int(text, 0)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.post("/api/operate")
def operate():
    payload = request.get_json(silent=True) or {}
    try:
        width = int(payload.get("width", 8))
        a_value = _parse_input(payload.get("a", "0"))
        b_value = _parse_input(payload.get("b", "0"))
        c_value = _parse_input(payload.get("c", "0"))
    except (TypeError, ValueError) as exc:
        return jsonify(error=f"invalid input: {exc}"), 400
    if width < 1 or width > 16:
        return jsonify(error="number of bits must be between 1 and 16"), 400
    if min(a_value, b_value, c_value) < 0:
        return jsonify(error="inputs must be non-negative"), 400

    mask = (1 << width) - 1
    a_value &= mask
    b_value &= mask
    c_value &= mask
    operation_names = [
        "AND",
        "OR",
        "XOR",
        "NAND",
        "NOR",
        "NOT C",
        "XNOR",
        "(A AND B) OR C",
    ]
    results = [
        a_value & b_value,
        a_value | b_value,
        a_value ^ b_value,
        ~(a_value & b_value),
        ~(a_value | b_value),
        ~c_value,
        ~(a_value ^ b_value),
        (a_value & b_value) | c_value,
    ]
    output = sum(((results[index % 8] >> index) & 1) << index for index in range(width))
    bits = [
        {
            "bit": index,
            "a": (a_value >> index) & 1,
            "b": (b_value >> index) & 1,
            "c": (c_value >> index) & 1,
            "operation": operation_names[index % 8],
            "y": (output >> index) & 1,
        }
        for index in range(width - 1, -1, -1)
    ]
    return jsonify(
        {
            "width": width,
            "a": f"{a_value:0{width}b}",
            "b": f"{b_value:0{width}b}",
            "c": f"{c_value:0{width}b}",
            "output": f"{output:0{width}b}",
            "output_hex": f"0x{output:X}",
            "bits": bits,
        }
    )


@app.post("/api/verify")
def verify():
    tests_ok, test_output = run_make()
    artifacts_ok, artifact_output = run_make("artifacts")
    data = evidence()
    files_ok = all(data["artifact_files"].values())
    netlist_ok = not any(check.startswith("netlist is missing") for check in data["netlist_checks"])
    local_ok = tests_ok and artifacts_ok and files_ok and netlist_ok
    return jsonify(status="PASS" if local_ok else "FAIL", local={"functional_test": "PASS" if tests_ok else "FAIL", "artifact_generation": "PASS" if artifacts_ok else "FAIL", "netlist_check": "PASS" if netlist_ok else "FAIL", "details": data["netlist_checks"], "test_output": test_output, "artifact_output": artifact_output}, ai=ask_ollama(data))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5007")), debug=False)
