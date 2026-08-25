from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request

from flask import Flask, jsonify, render_template


app = Flask(__name__)
PROJECT_DIR = Path(__file__).resolve().parent
ARTIFACTS = {
    "waveform": PROJECT_DIR / "rom.vcd",
    "netlist": PROJECT_DIR / "rom_netlist.v",
    "diagram": PROJECT_DIR / "rom.dot",
    "image": PROJECT_DIR / "rom.png",
}


def _run_make(target: str = "") -> tuple[bool, str]:
    result = subprocess.run(
        ["make"] + ([target] if target else []),
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
    checks = []
    for term in ["module rom", "address", "data", "64'h1122334455667788", "3'h7"]:
        if term not in text:
            checks.append(f"netlist is missing expected term: {term}")
    if not checks:
        checks.append("netlist contains the expected 3-bit ROM lookup logic")
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
        "Review this 3-bit, 8-entry combinational ROM evidence. Return exactly "
        "{\"verdict\":\"PASS\"} or {\"verdict\":\"FAIL\"}. "
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


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/verify")
def verify():
    tests_ok, test_output = _run_make()
    artifacts_ok, artifact_output = _run_make("artifacts")
    evidence = _evidence()
    files_ok = all(item["exists"] for item in evidence["artifact_files"].values())
    local_ok = tests_ok and artifacts_ok and files_ok and not any(
        check.startswith("netlist is missing") for check in evidence["netlist_checks"]
    )
    return jsonify(
        {
            "status": "PASS" if local_ok else "FAIL",
            "local": {
                "functional_test": "PASS" if tests_ok else "FAIL",
                "artifact_generation": "PASS" if artifacts_ok else "FAIL",
                "netlist_check": "PASS" if files_ok else "FAIL",
                "details": evidence["netlist_checks"],
                "test_output": test_output,
                "artifact_output": artifact_output,
            },
            "ai": _ask_ollama(evidence),
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5004")), debug=False)
