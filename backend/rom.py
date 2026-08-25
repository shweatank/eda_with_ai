from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
from openai import OpenAI
import json
import os
app = FastAPI()


# Connect OpenAI-compatible Python client to LOCAL Ollama server
client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

class Request(BaseModel):
    module: list[str]
    enabled: bool


@app.get("/")
def greeting():
    return {"message": "fine good starting"}


@app.post("/run-rom")
def decoder_module(data: Request):

    results = []
    
    # --------------------------------------------------
    # 1. Run Makefiles
    # --------------------------------------------------

    for module in data.module:

        makefile = f"{module}.mk"

        result = subprocess.run(
            ["make", "-f", f"MAKE_FILES/{makefile}"],
            cwd="..",
            capture_output=True,
            text=True
        )

        results.append({
            "module": module,
            "status": "success" if result.returncode == 0 else "failed",
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        })

    # --------------------------------------------------
    # 2. Create prompt for Ollama
    # --------------------------------------------------
    prompt = f"""
You are an EDA verification and synthesis analysis assistant.

Analyze the following RTL verification and synthesis results.

Generate a clean, professional, human-readable
EDA AI Verification Report suitable for displaying
in a terminal.

IMPORTANT:
- Do NOT return JSON.
- Do NOT use Markdown headings.
- Do NOT use ``` code blocks.
- Use plain text only.
- Do not invent information.
- Clearly distinguish warnings from failures.
- Base your analysis ONLY on the provided results.

REPORT FORMAT:

==================================================
             EDA AI VERIFICATION REPORT
==================================================

RTL MODULE
----------
Module       : rom
RTL File     : rtl/rom.sv

SIMULATION
----------
Simulator    : <simulator>
Tests        : <number>
Passed       : <number>
Failed       : <number>
Skipped      : <number>

Status       : <PASS/FAIL>

SYNTHESIS
---------
Tool         : Yosys
Top Module   : rom
Parsing      : <SUCCESS/FAILED>
Latch        : <NONE DETECTED / DETECTED>
Netlist      : <GENERATED / NOT GENERATED>

WARNINGS
--------
<List warnings>

AI ANALYSIS
-----------
<2-4 concise observations>

Recommendation:
<practical recommendation>

FINAL STATUS
------------
              <PASS/FAIL>
==================================================

EDA TOOL RESULTS:
{json.dumps(results, indent=2)}
"""
    # --------------------------------------------------
    # 3. Send results to LOCAL Ollama
    # --------------------------------------------------

    response = client.chat.completions.create(
         model="gemini-3.6-flash",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)
    # Get Gemini's generated report
    ai_analysis = response.choices[0].message.content
    print("\n" + ai_analysis)

    return {
    "status": "PASS",
    "ai_analysis": ai_analysis

}
