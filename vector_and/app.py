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
    "waveform": PROJECT_DIR / "vector_and.vcd",
    "netlist": PROJECT_DIR / "vector_and_netlist.v",
    "diagram": PROJECT_DIR / "vector_and.dot",
    "image": PROJECT_DIR / "vector_and.png",
}


def _run_make(target: str = "", width: int | None = None) -> tuple[bool, str]:
    if width is not None:
        clean = subprocess.run(
            ["make", "clean_vector_and"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if clean.returncode != 0:
            output = (clean.stdout + clean.stderr).strip()
            return False, output[-4000:]

    command = ["make"]
    if width is not None:
        command.append(f"WIDTH={width}")
    if target:
        command.append(target)
    result = subprocess.run(
        command,
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output[-4000:]


def _netlist_checks() -> list[str]:
    netlist = ARTIFACTS["netlist"]
    if not netlist.is_file():
        return ["netlist file is missing"]

    text = netlist.read_text(encoding="utf-8")
    source = (PROJECT_DIR / "vector_and.sv").read_text(encoding="utf-8")
    checks = []
    for term in ["module vector_and", "a", "b", "y"]:
        if term not in text:
            checks.append(f"netlist is missing expected term: {term}")
    for term in ["parameter WIDTH", "generate", "GEN_AND"]:
        if term not in source:
            checks.append(f"RTL source is missing expected term: {term}")
    if not checks:
        checks.append("RTL and netlist contain the expected generated vector AND logic")
    return checks


def _evidence() -> dict[str, object]:
    files = {
        name: {"exists": path.is_file(), "bytes": path.stat().st_size if path.is_file() else 0}
        for name, path in ARTIFACTS.items()
    }
    return {
        "rtl_test": "results.xml",
        "artifact_files": files,
        "netlist_checks": _netlist_checks(),
    }


def _ask_ollama(evidence: dict[str, object]) -> dict[str, str]:
    model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
    endpoint = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
    prompt = (
        "Review this parameterized generated vector AND evidence. Return exactly "
        '{"verdict":"PASS"} or {"verdict":"FAIL"}. '
        "No explanation outside JSON.\n\n" + json.dumps(evidence)
    )
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0, "num_predict": 8},
    }
    request = urllib_request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        timeout = float(os.getenv("OLLAMA_TIMEOUT", "15"))
        with urllib_request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        analysis = json.loads(body["response"])
        if analysis.get("verdict") not in {"PASS", "FAIL"}:
            raise ValueError("Ollama returned an invalid verdict")
        return {
            "source": f"ollama:{model}",
            "verdict": analysis["verdict"],
            "functionality": analysis["verdict"],
            "netlist": analysis["verdict"],
            "summary": "Compact Ollama review completed.",
        }
    except (OSError, ValueError, KeyError, json.JSONDecodeError, urllib_error.URLError) as exc:
        return {
            "source": "ollama-unavailable",
            "verdict": "FAIL",
            "functionality": "Ollama review was not completed.",
            "netlist": "Ollama review was not completed.",
            "summary": f"{exc}. Check Ollama and OLLAMA_MODEL.",
        }


def _parse_number(value: object) -> int:
    text = str(value).strip().replace("_", "")
    if not text:
        raise ValueError("input values cannot be empty")
    return int(text, 0)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/operate")
def operate():
    payload = request.get_json(silent=True) or {}
    try:
        width = int(payload.get("width", 8))
        a_value = _parse_number(payload.get("a", "0"))
        b_value = _parse_number(payload.get("b", "0"))
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"invalid input: {exc}"}), 400
    if width < 1 or width > 64:
        return jsonify({"error": "WIDTH must be between 1 and 64"}), 400
    if a_value < 0 or b_value < 0:
        return jsonify({"error": "inputs must be non-negative"}), 400

    mask = (1 << width) - 1
    masked_a = a_value & mask
    masked_b = b_value & mask
    output = masked_a & masked_b
    digits = (width + 3) // 4
    return jsonify(
        {
            "width": width,
            "mask": f"0b{mask:0{width}b}",
            "a": {"input": a_value, "hex": f"0x{masked_a:0{digits}X}", "binary": f"{masked_a:0{width}b}"},
            "b": {"input": b_value, "hex": f"0x{masked_b:0{digits}X}", "binary": f"{masked_b:0{width}b}"},
            "operation": f"{masked_a:0{width}b} AND {masked_b:0{width}b}",
            "output": {"decimal": output, "hex": f"0x{output:0{digits}X}", "binary": f"{output:0{width}b}"},
        }
    )


@app.post("/api/verify")
def verify():
    payload = request.get_json(silent=True) or {}
    widths = payload.get("widths", [1, 4, 8, 16])
    if not isinstance(widths, list) or not widths:
        return jsonify({"error": "widths must be a non-empty list"}), 400
    try:
        widths = [int(width) for width in widths]
    except (TypeError, ValueError):
        return jsonify({"error": "widths must contain integers"}), 400
    if any(width < 1 or width > 64 for width in widths):
        return jsonify({"error": "each WIDTH must be between 1 and 64"}), 400

    width_results = []
    for width in widths:
        passed, output = _run_make(width=width)
        width_results.append({"width": width, "status": "PASS" if passed else "FAIL", "output": output})

    tests_ok = all(item["status"] == "PASS" for item in width_results)
    test_output = "\n\n".join(f"WIDTH={item['width']}\n{item['output']}" for item in width_results)
    artifacts_ok, artifact_output = _run_make("artifacts")
    evidence = _evidence()
    evidence["width_results"] = [{"width": item["width"], "status": item["status"]} for item in width_results]
    files_ok = all(item["exists"] for item in evidence["artifact_files"].values())
    netlist_ok = not any(check.startswith("netlist is missing") for check in evidence["netlist_checks"])
    local_ok = tests_ok and artifacts_ok and files_ok and netlist_ok
    return jsonify(
        {
            "status": "PASS" if local_ok else "FAIL",
            "local": {
                "functional_test": "PASS" if tests_ok else "FAIL",
                "artifact_generation": "PASS" if artifacts_ok else "FAIL",
                "netlist_check": "PASS" if netlist_ok else "FAIL",
                "details": evidence["netlist_checks"],
                "width_results": width_results,
                "test_output": test_output,
                "artifact_output": artifact_output,
            },
            "ai": _ask_ollama(evidence),
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5006")), debug=False)
