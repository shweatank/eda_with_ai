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
ARTIFACTS = {
    "waveform": PROJECT_DIR / "ram.vcd",
    "netlist": PROJECT_DIR / "ram_netlist.v",
    "diagram": PROJECT_DIR / "ram.dot",
    "image": PROJECT_DIR / "ram.png",
}
MEMORY = {}


def run_make(target: str = "", data_width: int | None = None) -> tuple[bool, str]:
    if data_width is not None:
        clean = subprocess.run(["make", "clean_dynamic_ram"], cwd=PROJECT_DIR, capture_output=True, text=True, timeout=60)
        if clean.returncode != 0:
            return False, (clean.stdout + clean.stderr)[-4000:]
    command = ["make"]
    if data_width is not None:
        command.append(f"DATA_WIDTH={data_width}")
    if target:
        command.append(target)
    result = subprocess.run(command, cwd=PROJECT_DIR, capture_output=True, text=True, timeout=120, check=False)
    return result.returncode == 0, (result.stdout + result.stderr).strip()[-4000:]


def evidence() -> dict[str, object]:
    netlist = ARTIFACTS["netlist"]
    source = (PROJECT_DIR / "ram.sv").read_text(encoding="utf-8")
    text = netlist.read_text(encoding="utf-8") if netlist.is_file() else ""
    checks = []
    for term in ["module dynamic_ram", "memory", "write_enable", "read_data"]:
        if term not in text:
            checks.append(f"netlist is missing expected term: {term}")
    for term in ["parameter DATA_WIDTH", "parameter ADDRESS_WIDTH", "memory [0:", "posedge clk"]:
        if term not in source:
            checks.append(f"RTL source is missing expected term: {term}")
    if not checks:
        checks.append("RTL and netlist contain the parameterized synchronous RAM")
    return {"artifact_files": {name: {"exists": path.is_file(), "bytes": path.stat().st_size if path.is_file() else 0} for name, path in ARTIFACTS.items()}, "netlist_checks": checks}


def ask_ollama(data: dict[str, object]) -> dict[str, str]:
    model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
    endpoint = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
    payload = {"model": model, "prompt": "Review this dynamic-width synchronous RAM evidence. Return exactly {\"verdict\":\"PASS\"} or {\"verdict\":\"FAIL\"}.\n" + json.dumps(data), "stream": False, "format": "json", "options": {"temperature": 0, "num_predict": 8}}
    try:
        req = urllib_request.Request(endpoint, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
        with urllib_request.urlopen(req, timeout=float(os.getenv("OLLAMA_TIMEOUT", "15"))) as response:
            verdict = json.loads(json.loads(response.read().decode())["response"])["verdict"]
        return {"source": f"ollama:{model}", "verdict": verdict, "summary": "Ollama review completed."}
    except (OSError, ValueError, KeyError, json.JSONDecodeError, urllib_error.URLError) as exc:
        return {"source": "ollama-unavailable", "verdict": "FAIL", "summary": str(exc)}


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
        address_width = int(payload.get("address_width", 8))
        operation = str(payload.get("operation", "read")).lower()
        address = int(str(payload.get("address", "0")), 0)
        write_data = int(str(payload.get("write_data", "0")), 0)
    except (TypeError, ValueError) as exc:
        return jsonify(error=f"invalid input: {exc}"), 400
    if width not in {8, 16, 32, 64}:
        return jsonify(error="DATA_WIDTH must be 8, 16, 32, or 64"), 400
    if address_width not in {8, 10, 12, 16}:
        return jsonify(error="ADDRESS_WIDTH must be 8, 10, 12, or 16"), 400
    if operation not in {"read", "write"}:
        return jsonify(error="operation must be read or write"), 400
    max_address = (1 << address_width) - 1
    if address < 0 or address > max_address or write_data < 0:
        return jsonify(error=f"address must be 0-{max_address} and data must be non-negative"), 400
    mask = (1 << width) - 1
    key = (width, address_width)
    value = write_data & mask
    if operation == "write":
        MEMORY.setdefault(key, {})[address] = value
        output_value = value
        operation_text = f"memory[{address}] <= write_data"
    else:
        output_value = MEMORY.get(key, {}).get(address, 0)
        operation_text = f"read_data <= memory[{address}]"
    digits = width // 4
    return jsonify(width=width, address_width=address_width, depth=1 << address_width,
                   address=f"0x{address:0{(address_width + 3) // 4}X}", operation=operation,
                   input_hex=f"0x{write_data:X}", stored_hex=f"0x{value:0{digits}X}",
                   stored_binary=f"{value:0{width}b}", operation_text=operation_text,
                   output=f"read_data = 0x{output_value:0{digits}X}",
                   output_hex=f"0x{output_value:0{digits}X}", output_binary=f"{output_value:0{width}b}")


@app.post("/api/verify")
def verify():
    payload = request.get_json(silent=True) or {}
    widths = payload.get("widths", [8, 16, 32, 64])
    try:
        widths = [int(width) for width in widths]
    except (TypeError, ValueError):
        return jsonify(error="widths must contain integers"), 400
    if not widths or any(width not in {8, 16, 32, 64} for width in widths):
        return jsonify(error="widths must be selected from 8, 16, 32, 64"), 400
    results = []
    for width in widths:
        passed, output = run_make(data_width=width)
        results.append({"width": width, "status": "PASS" if passed else "FAIL", "output": output})
    tests_ok = all(item["status"] == "PASS" for item in results)
    artifacts_ok, artifact_output = run_make("artifacts")
    data = evidence()
    files_ok = all(item["exists"] for item in data["artifact_files"].values())
    netlist_ok = not any(check.startswith("netlist is missing") or check.startswith("RTL source is missing") for check in data["netlist_checks"])
    local_ok = tests_ok and artifacts_ok and files_ok and netlist_ok
    data["width_results"] = [{"width": item["width"], "status": item["status"]} for item in results]
    return jsonify(status="PASS" if local_ok else "FAIL", local={"functional_test": "PASS" if tests_ok else "FAIL", "artifact_generation": "PASS" if artifacts_ok else "FAIL", "netlist_check": "PASS" if netlist_ok else "FAIL", "width_results": results, "details": data["netlist_checks"], "test_output": "\n\n".join(f"DATA_WIDTH={item['width']}\n{item['output']}" for item in results), "artifact_output": artifact_output}, ai=ask_ollama(data))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5008")), debug=False)
