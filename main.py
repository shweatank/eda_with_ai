import asyncio
import os
import xml.etree.ElementTree as ET
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from google import genai
from pydantic import BaseModel

app = FastAPI(
    title="Verilog AI Studio",
    description="Automated runner and log viewer for SystemVerilog testbenches with AI Copilot",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
VERILOG_DIR = os.path.join(CURRENT_DIR, "Verilog")

api_key = os.environ.get("GEMINI_API_KEY")
ai_client = genai.Client(api_key=api_key) if api_key else None


class ModuleInfo(BaseModel):
    module: str
    files: List[str]
    has_script: bool


class GateExecutionResponse(BaseModel):
    gate: str
    status: str
    return_code: int
    stdout: str
    stderr: str
    passed: bool
    total_tests: Optional[int] = None


class ExplainRequest(BaseModel):
    module_name: str
    code: str
    simulation_log: str


def get_module_path(module_name: str) -> Optional[str]:
    """Resolves module folder from Verilog/ or directly under Documents/."""
    path_in_verilog = os.path.join(VERILOG_DIR, module_name)
    path_in_docs = os.path.join(CURRENT_DIR, module_name)

    if os.path.isdir(path_in_verilog):
        return path_in_verilog
    if os.path.isdir(path_in_docs):
        return path_in_docs
    return None


def parse_cocotb_results(results_xml_path: str):
    if not os.path.exists(results_xml_path):
        return None, None
    try:
        tree = ET.parse(results_xml_path)
        root = tree.getroot()
        testsuite = root if root.tag == "testsuite" else root.find("testsuite")
        if testsuite is not None:
            failures = int(testsuite.attrib.get("failures", 0))
            errors = int(testsuite.attrib.get("errors", 0))
            tests = int(testsuite.attrib.get("tests", 0))
            return (failures + errors == 0), tests
    except Exception:
        pass
    return None, None


@app.get("/api/modules", response_model=List[ModuleInfo])
async def list_modules():
    modules = []
    # 1. Scan Verilog/ folder
    if os.path.exists(VERILOG_DIR):
        for entry in sorted(os.listdir(VERILOG_DIR)):
            entry_path = os.path.join(VERILOG_DIR, entry)
            if os.path.isdir(entry_path) and not entry.startswith((".", "__")):
                files = [
                    f for f in os.listdir(entry_path) if not f.startswith(".")
                ]
                has_runner = "run.bash" in files or "Makefile" in files
                modules.append(
                    ModuleInfo(module=entry, files=files, has_script=has_runner)
                )

    # 2. Check for signed_alu directly in Documents/
    signed_alu_path = os.path.join(CURRENT_DIR, "signed_alu")
    if os.path.isdir(signed_alu_path):
        files = [
            f for f in os.listdir(signed_alu_path) if not f.startswith(".")
        ]
        has_runner = "run.bash" in files or "Makefile" in files
        if not any(m.module == "signed_alu" for m in modules):
            modules.append(
                ModuleInfo(
                    module="signed_alu", files=files, has_script=has_runner
                )
            )

    return modules


@app.get("/api/modules/{module_name}/files/{file_name}")
async def get_file_content(module_name: str, file_name: str):
    module_folder = get_module_path(module_name)
    if not module_folder:
        raise HTTPException(
            status_code=404, detail=f"Module '{module_name}' not found"
        )

    file_path = os.path.join(module_folder, file_name)

    # Fallback to shared all_gates.sv if file not found locally
    if not os.path.exists(file_path):
        shared_file = os.path.join(VERILOG_DIR, file_name)
        if os.path.exists(shared_file):
            file_path = shared_file
        else:
            raise HTTPException(
                status_code=404, detail=f"File '{file_name}' not found"
            )

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    return {"module": module_name, "file": file_name, "content": content}


@app.post(
    "/api/modules/{module_name}/run", response_model=GateExecutionResponse
)
async def run_module_testbench(module_name: str):
    module_folder = get_module_path(module_name)
    if not module_folder:
        raise HTTPException(
            status_code=404, detail=f"Module '{module_name}' not found"
        )

    if os.path.exists(os.path.join(module_folder, "run.bash")):
        cmd = ["bash", "run.bash"]
    elif os.path.exists(os.path.join(module_folder, "Makefile")):
        cmd = ["make", "-B"]
    else:
        raise HTTPException(
            status_code=400,
            detail=f"No 'run.bash' or 'Makefile' found in '{module_name}'",
        )

    env = os.environ.copy()
    env["SIM"] = "icarus"
    env["TOPLEVEL_LANG"] = "verilog"

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=module_folder,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(), timeout=45.0
        )
    except asyncio.TimeoutError:
        proc.kill()
        raise HTTPException(
            status_code=408, detail="Simulation timed out after 45 seconds"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    stdout_str = stdout_bytes.decode(errors="replace")
    stderr_str = stderr_bytes.decode(errors="replace")

    xml_path = os.path.join(module_folder, "results.xml")
    passed, total = parse_cocotb_results(xml_path)

    if passed is None:
        passed = proc.returncode == 0

    return GateExecutionResponse(
        gate=module_name,
        status="success" if proc.returncode == 0 else "failed",
        return_code=proc.returncode,
        stdout=stdout_str,
        stderr=stderr_str,
        passed=passed,
        total_tests=total,
    )


@app.post("/api/ai/analyze")
async def ai_analyze(req: ExplainRequest):
    if not ai_client:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured on the server.",
        )

    prompt = f"""
    You are an expert Digital Design & SystemVerilog verification engineer.
    Analyze the following hardware module ({req.module_name}) and its Cocotb simulation run.

    Module Name: {req.module_name}

    === RTL Source Code ===
    {req.code}

    === Simulation Output Log ===
    {req.simulation_log}

    Provide:
    1. A concise verdict (Did it pass or fail? Why?).
    2. A brief 2-sentence explanation of what the logic does.
    3. If there are warnings/errors, explain how to fix them.
    4. Format your output cleanly in Markdown.
    """

    try:
        response = await asyncio.to_thread(
            ai_client.models.generate_content,
            model="gemini-3.6-flash",
            contents=prompt,
        )
        return {"analysis": response.text}
    except Exception as e:
        print(f"AI Generation Error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Gemini API Error: {str(e)}"
        )


@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <title>Verilog AI Studio</title>
      <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
      <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b0f19; color: #e2e8f0; margin: 0; padding: 24px; }
        .container { max-width: 1000px; margin: 0 auto; }
        h1 { color: #38bdf8; margin-bottom: 4px; }
        .subtitle { color: #94a3b8; margin-top: 0; margin-bottom: 20px; }
        .btn-group { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        button { background: #0284c7; color: white; border: none; padding: 10px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; transition: 0.2s; }
        button:hover { background: #0369a1; }
        .ai-btn { background: linear-gradient(135deg, #8b5cf6, #ec4899); }
        .ai-btn:hover { opacity: 0.9; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        .card { background: #1e293b; border-radius: 8px; padding: 16px; border: 1px solid #334155; }
        pre { background: #020617; border: 1px solid #1e293b; padding: 12px; border-radius: 6px; overflow-x: auto; color: #a5f3fc; font-family: monospace; font-size: 12px; height: 260px; }
        .ai-box { background: #181b2a; border: 1px solid #6366f1; border-radius: 8px; padding: 16px; margin-top: 16px; line-height: 1.5; font-size: 14px; }
        .status-badge { display: inline-block; padding: 4px 10px; border-radius: 4px; font-weight: bold; margin-bottom: 8px; font-size: 12px; }
        .status-pass { background: #16a34a; }
        .status-fail { background: #dc2626; }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>⚡ Verilog AI Studio</h1>
        <p class="subtitle">Hardware Simulation & Verification Copilot</p>
        
        <div id="buttons" class="btn-group">Loading modules...</div>

        <div class="grid">
          <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <h3 style="margin:0;">Terminal Output</h3>
              <span id="badge" class="status-badge" style="display:none;"></span>
            </div>
            <pre id="console-output">// Run a module to inspect stdout/stderr logs...</pre>
          </div>

          <div class="card">
            <h3 id="code-header" style="margin:0;">RTL Source Code</h3>
            <pre id="code-output">// Source code will load here...</pre>
          </div>
        </div>

        <div style="margin-top: 16px;">
          <button id="ai-trigger" class="ai-btn" style="display:none;" onclick="triggerAIAnalysis()">✨ Analyze & Debug with AI</button>
        </div>

        <div id="ai-container" class="ai-box" style="display:none;">
          <div id="ai-content">Generating analysis...</div>
        </div>
      </div>

      <script>
        let currentModule = '';
        let lastOutput = '';
        let lastCode = '';

        async function loadModules() {
          const res = await fetch('/api/modules');
          const modules = await res.json();
          const btnContainer = document.getElementById('buttons');
          btnContainer.innerHTML = '';

          modules.forEach(m => {
            const btn = document.createElement('button');
            btn.innerText = `Run ${m.module}`;
            btn.onclick = () => runModule(m.module);
            btnContainer.appendChild(btn);
          });
        }

        async function fetchSourceCode(moduleName) {
          // Check for alu.sv, all_gates.sv, module-specific .sv or .v
          const possibleFiles = ['alu.sv', `${moduleName}.sv`, 'all_gates.sv', `${moduleName}.v`];
          for (const filename of possibleFiles) {
            try {
              const res = await fetch(`/api/modules/${moduleName}/files/${filename}`);
              if (res.ok) {
                const data = await res.json();
                document.getElementById('code-header').innerText = `RTL Source Code (${filename})`;
                return data.content;
              }
            } catch (e) {}
          }
          return '// Could not load RTL source file.';
        }

        async function runModule(moduleName) {
          currentModule = moduleName;
          const out = document.getElementById('console-output');
          const codeEl = document.getElementById('code-output');
          const badge = document.getElementById('badge');
          const aiBtn = document.getElementById('ai-trigger');
          const aiContainer = document.getElementById('ai-container');

          aiContainer.style.display = 'none';
          badge.style.display = 'inline-block';
          badge.className = 'status-badge';
          badge.innerText = 'Running...';
          out.innerText = `Simulating ${moduleName}...`;

          // 1. Fetch Source Code
          lastCode = await fetchSourceCode(moduleName);
          codeEl.innerText = lastCode;

          // 2. Execute Simulation
          try {
            const res = await fetch(`/api/modules/${moduleName}/run`, { method: 'POST' });
            const data = await res.json();

            badge.className = data.passed ? 'status-badge status-pass' : 'status-badge status-fail';
            badge.innerText = data.passed ? 'PASSED' : 'FAILED';
            
            lastOutput = data.stdout || data.stderr;
            out.innerText = lastOutput;
            aiBtn.style.display = 'inline-block';
          } catch (err) {
            badge.className = 'status-badge status-fail';
            badge.innerText = 'ERROR';
            out.innerText = 'Failed to execute API request.';
          }
        }

        async function triggerAIAnalysis() {
          const aiContainer = document.getElementById('ai-container');
          const aiContent = document.getElementById('ai-content');
          aiContainer.style.display = 'block';
          aiContent.innerHTML = '<em>🧠 AI Copilot is inspecting the RTL code and simulation logs...</em>';

          try {
            const res = await fetch('/api/ai/analyze', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                module_name: currentModule,
                code: lastCode,
                simulation_log: lastOutput
              })
            });
            const data = await res.json();
            if (!res.ok) {
              throw new Error(data.detail || 'Server error');
            }
            aiContent.innerHTML = marked.parse(data.analysis);
          } catch (err) {
            aiContent.innerHTML = `<span style="color: #f87171;">⚠️ ${err.message}</span>`;
          }
        }

        loadModules();
      </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)