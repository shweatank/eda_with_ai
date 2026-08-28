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
    "waveform": PROJECT_DIR / "fifo.vcd",
    "netlist": PROJECT_DIR / "fifo_netlist.v",
    "diagram": PROJECT_DIR / "fifo.dot",
    "image": PROJECT_DIR / "fifo.png",
}
MEMORY = {}


def run_make(target: str = "", data_width: int = 8, fifo_depth: int = 8) -> tuple[bool, str]:
    if target == "":
        subprocess.run(["make", "clean_fifo"], cwd=PROJECT_DIR, capture_output=True, text=True, check=False)
    command = ["make", f"DATA_WIDTH={data_width}", f"FIFO_DEPTH={fifo_depth}"]
    if target:
        command.append(target)
    result = subprocess.run(command, cwd=PROJECT_DIR, capture_output=True, text=True, timeout=120, check=False)
    return result.returncode == 0, (result.stdout + result.stderr).strip()[-4000:]


def evidence() -> dict[str, object]:
    source = (PROJECT_DIR / "fifo.sv").read_text(encoding="utf-8")
    netlist = ARTIFACTS["netlist"].read_text(encoding="utf-8") if ARTIFACTS["netlist"].is_file() else ""
    checks = []
    for term in ["parameter DATA_WIDTH", "parameter FIFO_DEPTH", "memory", "full", "empty", "overflow", "underflow"]:
        if term not in source:
            checks.append(f"RTL source is missing expected term: {term}")
    for term in ["module parameterized_fifo(", "write_data", "read_data"]:
        if term not in netlist:
            checks.append(f"netlist is missing expected term: {term}")
    if not checks:
        checks.append("RTL and netlist contain the parameterized synchronous FIFO")
    return {"artifact_files": {name: path.is_file() for name, path in ARTIFACTS.items()}, "netlist_checks": checks}


def ask_ollama(data: dict[str, object]) -> dict[str, str]:
    model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
    endpoint = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
    payload = {"model": model, "prompt": "Review this parameterized synchronous FIFO evidence. Return exactly {\"verdict\":\"PASS\"} or {\"verdict\":\"FAIL\"}.\n" + json.dumps(data), "stream": False, "format": "json", "options": {"temperature": 0, "num_predict": 8}}
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
        data_width = int(payload.get("data_width", 8))
        fifo_depth = int(payload.get("fifo_depth", 8))
        operation = str(payload.get("operation", "read"))
        value = int(str(payload.get("value", "0")), 0)
    except (TypeError, ValueError) as exc:
        return jsonify(error=f"invalid input: {exc}"), 400
    if data_width not in {8, 16, 32, 64} or fifo_depth not in {4, 8, 16, 32, 64}:
        return jsonify(error="choose data width 8/16/32/64 and FIFO depth 4/8/16/32/64"), 400
    if operation not in {"write", "read", "status", "reset"}:
        return jsonify(error="operation must be write, read, status, or reset"), 400
    key = (data_width, fifo_depth)
    queue = MEMORY.setdefault(key, [])
    mask = (1 << data_width) - 1
    if operation == "reset":
        queue.clear()
    elif operation == "write":
        if len(queue) >= fifo_depth:
            return jsonify(error="FIFO is full", data_width=data_width, fifo_depth=fifo_depth, count=len(queue), full=True), 409
        queue.append(value & mask)
    elif operation == "read":
        if not queue:
            return jsonify(error="FIFO is empty", data_width=data_width, fifo_depth=fifo_depth, count=0, empty=True), 409
        value = queue.pop(0)
    return jsonify(operation=operation, data_width=data_width, fifo_depth=fifo_depth, count=len(queue), full=len(queue) == fifo_depth, empty=not queue, value=f"0x{value & mask:0{data_width // 4}X}", binary=f"{value & mask:0{data_width}b}", queue=[f"0x{item:0{data_width // 4}X}" for item in queue])


@app.post("/api/verify")
def verify():
    payload = request.get_json(silent=True) or {}
    configurations = payload.get("configurations", [{"data_width": 8, "fifo_depth": 8}, {"data_width": 16, "fifo_depth": 16}, {"data_width": 32, "fifo_depth": 32}, {"data_width": 64, "fifo_depth": 64}])
    results = []
    for config in configurations:
        width, depth = int(config["data_width"]), int(config["fifo_depth"])
        passed, output = run_make(data_width=width, fifo_depth=depth)
        results.append({"data_width": width, "fifo_depth": depth, "status": "PASS" if passed else "FAIL", "output": output})
    artifacts_ok, artifact_output = run_make("artifacts")
    data = evidence()
    netlist_ok = not data["netlist_checks"] or not any("missing" in check for check in data["netlist_checks"])
    local_ok = all(item["status"] == "PASS" for item in results) and artifacts_ok and all(data["artifact_files"].values()) and netlist_ok
    data["configurations"] = [{"data_width": item["data_width"], "fifo_depth": item["fifo_depth"], "status": item["status"]} for item in results]
    return jsonify(status="PASS" if local_ok else "FAIL", local={"functional_test": "PASS" if all(item["status"] == "PASS" for item in results) else "FAIL", "artifact_generation": "PASS" if artifacts_ok else "FAIL", "netlist_check": "PASS" if netlist_ok else "FAIL", "configurations": results, "details": data["netlist_checks"], "test_output": "\n\n".join(item["output"] for item in results), "artifact_output": artifact_output}, ai=ask_ollama(data))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5009")), debug=False)
