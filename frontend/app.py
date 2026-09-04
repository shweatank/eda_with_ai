"""
Streamlit dashboard for the AI-Powered RTL Verification & Debugging Platform.

    streamlit run frontend/app.py

The UI talks to FastAPI **only** over GraphQL (never directly to Neo4j).
"""
from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests
import streamlit as st

# ---------------------------------------------------------------------
# configuration
# ---------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

try:                                    # optional: read GRAPHQL_URL from .env
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:                     # pragma: no cover
    pass

GRAPHQL_URL = os.getenv("GRAPHQL_URL", "http://localhost:8000/graphql")
HEALTH_URL = GRAPHQL_URL.replace("/graphql", "/health")

PROJECT_ID = "P001"
PROJECT_NAME = "Traffic Light and ALU Verification"
PROJECT_DESCRIPTION = (
    "SystemVerilog RTL verification with Icarus Verilog, Neo4j AuraDB and Groq"
)

EXAMPLE_LABELS = {
    "Traffic Light Controller": "traffic_light",
    "4-bit ALU": "alu",
}
SCENARIO_LABELS = {"Passing": "passing", "Failing": "failing"}

TERMINAL_STATES = ("COMPLETED", "FAILED")
POLL_INTERVAL_SECONDS = 1.0
POLL_TIMEOUT_SECONDS = 180

st.set_page_config(
    page_title="AI-Powered RTL Verification & Debugging Platform",
    page_icon="🔬",
    layout="wide",
)


# =====================================================================
# GraphQL client
# =====================================================================
class GraphQLError(RuntimeError):
    pass


def gql(query: str, variables: Optional[Dict[str, Any]] = None,
        timeout: int = 120) -> Dict[str, Any]:
    """POST a GraphQL document and return `data`, raising on any error."""
    try:
        response = requests.post(
            GRAPHQL_URL,
            json={"query": query, "variables": variables or {}},
            timeout=timeout,
        )
    except requests.exceptions.ConnectionError as exc:
        raise GraphQLError(
            f"Cannot reach the backend at {GRAPHQL_URL}.\n\n"
            "Start it with:\n"
            "`uvicorn backend.main:app --reload --port 8000`"
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise GraphQLError(
            f"The backend did not respond within {timeout}s."
        ) from exc

    if response.status_code != 200:
        raise GraphQLError(
            f"Backend returned HTTP {response.status_code}: "
            f"{response.text[:400]}"
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise GraphQLError(
            f"Backend returned a non-JSON response: {response.text[:400]}"
        ) from exc

    if payload.get("errors"):
        messages = "; ".join(
            e.get("message", "unknown error") for e in payload["errors"]
        )
        raise GraphQLError(f"GraphQL error: {messages}")

    return payload.get("data") or {}


def backend_health() -> Optional[Dict[str, Any]]:
    try:
        r = requests.get(HEALTH_URL, timeout=10)
        return r.json() if r.status_code == 200 else None
    except requests.RequestException:
        return None


# =====================================================================
# GraphQL documents
# =====================================================================
CREATE_PROJECT = """
mutation CreateProject($projectId: String!, $name: String!, $description: String!) {
  createProject(projectId: $projectId, name: $name, description: $description) {
    projectId
    name
    createdAt
  }
}
"""

RUN_VERIFICATION = """
mutation RunVerification($projectId: String!, $example: String!, $scenario: String!) {
  runVerification(projectId: $projectId, example: $example, scenario: $scenario) {
    jobId
    status
    progress
  }
}
"""

JOB_STATUS = """
query JobStatus($jobId: String!) {
  verificationJob(jobId: $jobId) {
    jobId
    status
    progress
    errorMessage
  }
}
"""

VERIFICATION_RESULT = """
query VerificationResult($jobId: String!) {
  verificationResult(jobId: $jobId) {
    jobId
    projectId
    projectName
    example
    scenario
    status
    progress
    errorMessage
    rtlModule    { moduleName fileName filePath }
    testbench    { fileName filePath }
    simulation   { simulationId status totalTests passedTests failedTests duration }
    waveform     { fileName filePath }
    tests        { testId name status expected actual message }
    failures     { failureId category severity expected actual message testId testName }
    aiAnalyses   { rootCause explanation recommendation confidence }
    traceability { level label value }
    simulationLog
  }
}
"""


# =====================================================================
# GTKWave launcher
# =====================================================================
# GTKWave is a desktop application, so it can only be launched when
# Streamlit is running on the same machine as the display. That is the
# normal local-demo setup. It stays entirely optional: the platform never
# needs GTKWave to produce a result.

VIEWS_DIR = PROJECT_ROOT / "waveform_views"

# The VS Code snap exports GTK/library paths that break a system-installed
# gtkwave with a GLIBC symbol error. Streamlit inherits them when it is
# started from the VS Code terminal, so strip them for the child process.
_SNAP_VARS = (
    "SNAP", "SNAP_NAME", "SNAP_REVISION", "SNAP_INSTANCE_NAME",
    "SNAP_VERSION", "SNAP_ARCH", "SNAP_LIBRARY_PATH",
    "GTK_PATH", "GTK_EXE_PREFIX", "GDK_PIXBUF_MODULE_FILE",
    "GIO_MODULE_DIR", "GSETTINGS_SCHEMA_DIR", "LOCPATH",
    "LD_LIBRARY_PATH",
)


def _has_display() -> bool:
    """True when a desktop session is reachable from this process."""
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def _view_file_for(example: str) -> Optional[Path]:
    """The .gtkw session file that pre-loads the interesting signals."""
    candidate = VIEWS_DIR / f"{(example or '').strip().lower()}.gtkw"
    return candidate if candidate.is_file() else None


def launch_gtkwave(vcd_path: str, example: str = "") -> Tuple[bool, str]:
    """
    Open a VCD in GTKWave as a separate desktop window.

    Returns (ok, message). Never raises and never blocks Streamlit: the
    viewer is started detached, so it keeps running after this returns.
    """
    if not vcd_path:
        return False, "No waveform file is recorded for this job."

    vcd = Path(vcd_path)
    if not vcd.is_file():
        return False, (
            f"The waveform file no longer exists on disk:\n\n`{vcd}`\n\n"
            "Re-run the verification to regenerate it."
        )

    binary = shutil.which("gtkwave")
    if binary is None:
        return False, (
            "GTKWave is not installed, so the waveform cannot be opened "
            "here. Install it with:\n\n`sudo apt install gtkwave`\n\n"
            "The VCD file itself is already generated and can be opened on "
            "any machine that has GTKWave."
        )

    if not _has_display():
        return False, (
            "No desktop display is available to this Streamlit process "
            "(neither DISPLAY nor WAYLAND_DISPLAY is set), so a GTKWave "
            "window cannot be shown. Open it from a terminal on the "
            f"desktop instead:\n\n`gtkwave {vcd}`"
        )

    command = [binary, str(vcd)]
    view = _view_file_for(example)
    if view is not None:
        command.append(str(view))

    env = {k: v for k, v in os.environ.items() if k not in _SNAP_VARS}

    try:
        subprocess.Popen(                       # noqa: S603 - fixed argv, shell=False
            command,
            shell=False,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,             # survives a Streamlit rerun
        )
    except OSError as exc:
        return False, f"Could not start GTKWave: {exc}"

    detail = f" with the {view.name} signal view" if view is not None else ""
    return True, (
        f"GTKWave is opening in a separate desktop window{detail}. "
        "If you do not see it, check behind your browser window."
    )


# =====================================================================
# rendering helpers
# =====================================================================
SEVERITY_COLORS = {
    "LOW": "#3b82f6",
    "MEDIUM": "#f59e0b",
    "HIGH": "#ef4444",
    "CRITICAL": "#991b1b",
}


def render_sidebar() -> None:
    st.sidebar.header("Backend")
    st.sidebar.caption(f"GraphQL endpoint: `{GRAPHQL_URL}`")

    health = backend_health()
    if health is None:
        st.sidebar.error("Backend unreachable")
        st.sidebar.code("uvicorn backend.main:app --reload --port 8000", language="bash")
        return

    st.sidebar.success("FastAPI: ok")

    neo = health.get("neo4j", "unknown")
    if neo == "connected":
        st.sidebar.success("Neo4j AuraDB: connected")
    else:
        st.sidebar.error(f"Neo4j AuraDB: {neo}")
        if health.get("neo4j_error"):
            st.sidebar.caption(health["neo4j_error"])

    groq = health.get("groq", "unknown")
    if groq == "configured":
        st.sidebar.success(f"Groq: {health.get('groq_model', 'configured')}")
    else:
        st.sidebar.warning("Groq: not configured (set GROQ_API_KEY in .env)")

    iverilog = health.get("iverilog", "unknown")
    if "not found" in iverilog.lower():
        st.sidebar.error(f"Icarus Verilog: {iverilog}")
    else:
        st.sidebar.success(f"Icarus Verilog: {iverilog}")

    st.sidebar.divider()
    st.sidebar.header("Flow")
    st.sidebar.markdown(
        "Streamlit → GraphQL → FastAPI → Verification Service → "
        "**Icarus Verilog** → Simulation → Log Parser → PASS/FAIL → "
        "**Neo4j AuraDB** → (if FAIL) **Groq AI** → GraphQL → Streamlit"
    )


def render_summary(simulation: Optional[Dict[str, Any]]) -> None:
    st.subheader("Verification Summary")
    if not simulation:
        st.info("No simulation record yet.")
        return

    total = simulation.get("totalTests") or 0
    passed = simulation.get("passedTests") or 0
    failed = simulation.get("failedTests") or 0
    status = simulation.get("status") or "UNKNOWN"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Tests", total)
    c2.metric("Passed", passed)
    c3.metric("Failed", failed)
    c4.metric("Duration", f"{simulation.get('duration') or 0:.3f} s")

    if status == "PASSED":
        st.success(f"Status: **{status}** — {passed}/{total} tests passed")
    else:
        st.error(f"Status: **{status}** — {failed} of {total} tests failed")


def render_tests(tests: list) -> None:
    """Show EVERY test, passed and failed. Nothing is hidden."""
    st.subheader("Test Results")
    if not tests:
        st.info("No test results were parsed from the simulation log.")
        return

    for test in tests:
        passed = test.get("status") == "PASS"
        icon = "✓" if passed else "✗"
        title = f"{icon}  {test.get('testId','')} — {test.get('name','')} — {test.get('status','')}"

        if passed:
            st.markdown(
                f"<div style='padding:8px 12px;margin-bottom:6px;border-left:5px solid #16a34a;"
                f"background:rgba(22,163,74,0.10);border-radius:4px;'>"
                f"<b>{icon} {test.get('testId','')} — {test.get('name','')}</b>"
                f"&nbsp;&nbsp;<span style='color:#16a34a;font-weight:600;'>PASS</span><br>"
                f"<span style='font-size:0.85em;opacity:0.85;'>expected "
                f"<code>{test.get('expected','')}</code> · actual "
                f"<code>{test.get('actual','')}</code></span></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='padding:8px 12px;margin-bottom:6px;border-left:5px solid #dc2626;"
                f"background:rgba(220,38,38,0.10);border-radius:4px;'>"
                f"<b>{icon} {test.get('testId','')} — {test.get('name','')}</b>"
                f"&nbsp;&nbsp;<span style='color:#dc2626;font-weight:600;'>FAIL</span><br>"
                f"<span style='font-size:0.85em;opacity:0.85;'>expected "
                f"<code>{test.get('expected','')}</code> · actual "
                f"<code>{test.get('actual','')}</code></span></div>",
                unsafe_allow_html=True,
            )
        if test.get("message"):
            st.caption(f"&nbsp;&nbsp;&nbsp;{test['message']}")


def render_failures(failures: list) -> None:
    """Only shown when failures exist."""
    if not failures:
        return
    st.subheader("Failure Details")
    st.caption(
        "Category and severity are assigned by deterministic rules in "
        "`failure_analyzer.py` — not by the AI."
    )
    for failure in failures:
        severity = failure.get("severity", "MEDIUM")
        color = SEVERITY_COLORS.get(severity, "#6b7280")
        with st.container(border=True):
            c1, c2 = st.columns([1, 1])
            c1.markdown(f"**Failure Category**\n\n`{failure.get('category','')}`")
            c2.markdown(
                f"**Severity**\n\n<span style='background:{color};color:white;"
                f"padding:2px 10px;border-radius:10px;font-weight:600;'>"
                f"{severity}</span>",
                unsafe_allow_html=True,
            )
            c3, c4 = st.columns([1, 1])
            c3.markdown(f"**Expected**\n\n`{failure.get('expected','')}`")
            c4.markdown(f"**Actual**\n\n`{failure.get('actual','')}`")
            st.markdown(f"**Message**\n\n{failure.get('message','')}")
            st.caption(
                f"Test: {failure.get('testId','')} "
                f"({failure.get('testName','')}) · "
                f"Failure id: {failure.get('failureId','')}"
            )


def render_ai(analyses: list) -> None:
    if not analyses:
        return
    st.subheader("AI Root Cause Analysis")
    st.caption(
        "Produced by Groq from the real simulation evidence. The AI explains "
        "the failure — it never decides PASS/FAIL."
    )
    for i, analysis in enumerate(analyses, 1):
        with st.container(border=True):
            st.markdown(f"**Analysis {i} — Root Cause**")
            st.info(analysis.get("rootCause", ""))
            st.markdown("**Explanation**")
            st.write(analysis.get("explanation", ""))
            st.markdown("**Recommendation**")
            st.success(analysis.get("recommendation", ""))
            confidence = float(analysis.get("confidence") or 0.0)
            st.markdown(f"**Confidence: {confidence:.0%}**")
            st.progress(min(max(confidence, 0.0), 1.0))


def render_trace(trace: list) -> None:
    st.subheader("Neo4j Traceability")
    if not trace:
        st.info("No traceability data available for this job.")
        return
    st.caption(
        "Read back out of Neo4j AuraDB with a single Cypher traversal: "
        "Project → RTLModule → Testbench → VerificationJob → Simulation → "
        "Test → Failure → AIAnalysis"
    )
    lines = []
    for i, step in enumerate(sorted(trace, key=lambda s: s.get("level", 0))):
        if i:
            lines.append("        ↓")
        lines.append(f"  {step.get('label','')}: {step.get('value','')}")
    st.code("\n".join(lines), language="text")


def render_artifacts(result: Dict[str, Any]) -> None:
    st.subheader("Waveform & Artifacts")
    waveform = result.get("waveform") or {}
    vcd_path = waveform.get("filePath")

    if vcd_path:
        st.markdown("**Generated VCD waveform**")
        st.code(vcd_path, language="text")

        col_btn, col_note = st.columns([1, 2])
        with col_btn:
            open_clicked = st.button(
                "OPEN IN GTKWAVE",
                key=f"gtkwave_{result.get('jobId','')}",
                use_container_width=True,
                help="Launches GTKWave as a separate desktop window",
            )
        with col_note:
            if _has_display():
                st.caption(
                    "Opens as a separate desktop window, with the signals "
                    "for this example pre-loaded."
                )
            else:
                st.caption(
                    "No desktop display detected — use the command below "
                    "on the machine with the screen."
                )

        if open_clicked:
            ok, message = launch_gtkwave(vcd_path, result.get("example", ""))
            if ok:
                st.success(message)
            else:
                st.error(message)

        with st.expander("Or open it yourself from a terminal"):
            st.code(f"gtkwave {vcd_path}", language="bash")
            st.markdown(
                "The project also ships a launcher that pre-loads the "
                "signals and works from inside the VS Code terminal:"
            )
            example = (result.get("example") or "").strip().lower()
            scenario = (result.get("scenario") or "").strip().lower()
            st.code(
                f"./scripts/view_waveform.sh {example} {scenario}".rstrip(),
                language="bash",
            )
        st.caption(
            "GTKWave is only a viewer — it is not required for the platform "
            "to run."
        )
    else:
        st.warning("No waveform.vcd was recorded for this job.")

    rtl = result.get("rtlModule") or {}
    tb = result.get("testbench") or {}
    with st.expander("Source files used"):
        st.markdown(
            f"- **RTL module:** `{rtl.get('moduleName','?')}` — "
            f"`{rtl.get('filePath','?')}`\n"
            f"- **Testbench:** `{tb.get('filePath','?')}`"
        )

    log_text = result.get("simulationLog") or ""
    with st.expander("Raw simulation log (vvp stdout — the source of truth)"):
        if log_text.strip():
            st.code(log_text, language="text")
        else:
            st.caption(
                "The raw log is held by the backend worker process. "
                "It is also written to `data/jobs/<jobId>/simulation.log`."
            )


# =====================================================================
# main
# =====================================================================
def main() -> None:
    st.title("AI-Powered RTL Verification & Debugging Platform")
    st.caption(
        "SystemVerilog → Icarus Verilog → Simulation → Log Parser → "
        "PASS/FAIL → Neo4j AuraDB → Groq AI → GraphQL → Streamlit"
    )

    render_sidebar()

    # ---------------- project ----------------
    st.header("Project")
    st.text_input("Project Name", value=PROJECT_NAME, disabled=True)
    st.caption(f"Project id: `{PROJECT_ID}`")

    # ---------------- selection ----------------
    st.header("Run a Verification")
    col1, col2 = st.columns(2)
    with col1:
        example_label = st.selectbox("Select Example", list(EXAMPLE_LABELS.keys()))
    with col2:
        scenario_label = st.selectbox("Select Scenario", list(SCENARIO_LABELS.keys()))

    example = EXAMPLE_LABELS[example_label]
    scenario = SCENARIO_LABELS[scenario_label]

    if scenario == "failing":
        st.warning(
            "The **failing** scenario contains an intentional bug in the RTL "
            "only. The testbench is identical to the passing scenario."
        )

    run_clicked = st.button("RUN VERIFICATION", type="primary", use_container_width=True)

    # ---------------- run + poll ----------------
    if run_clicked:
        st.session_state.pop("result", None)
        st.session_state.pop("job_id", None)

        try:
            gql(
                CREATE_PROJECT,
                {
                    "projectId": PROJECT_ID,
                    "name": PROJECT_NAME,
                    "description": PROJECT_DESCRIPTION,
                },
            )
            job = gql(
                RUN_VERIFICATION,
                {"projectId": PROJECT_ID, "example": example, "scenario": scenario},
            )["runVerification"]
        except GraphQLError as exc:
            st.error(str(exc))
            st.stop()

        job_id = job["jobId"]
        st.session_state["job_id"] = job_id

        st.header("Job Status")
        info_box = st.empty()
        progress_bar = st.progress(0)

        status = job["status"]
        progress = job.get("progress") or 0
        error_message = None
        deadline = time.time() + POLL_TIMEOUT_SECONDS

        # poll every ~1s until COMPLETED or FAILED
        while True:
            info_box.info(
                f"**Job ID:** `{job_id}`  \n"
                f"**Status:** `{status}`  \n"
                f"**Progress:** {progress}%"
            )
            progress_bar.progress(min(max(progress, 0), 100))

            if status in TERMINAL_STATES:
                break
            if time.time() > deadline:
                error_message = (
                    f"Timed out after {POLL_TIMEOUT_SECONDS}s waiting for the job."
                )
                break

            time.sleep(POLL_INTERVAL_SECONDS)
            try:
                snapshot = gql(JOB_STATUS, {"jobId": job_id})["verificationJob"]
            except GraphQLError as exc:
                error_message = str(exc)
                break
            if snapshot is None:
                error_message = f"Job `{job_id}` disappeared from the backend."
                break
            status = snapshot["status"]
            progress = snapshot.get("progress") or 0
            error_message = snapshot.get("errorMessage")

        if error_message and status != "COMPLETED":
            st.error(f"Job problem: {error_message}")
        elif error_message:
            st.warning(f"Job completed with warnings: {error_message}")

        try:
            result = gql(VERIFICATION_RESULT, {"jobId": job_id})["verificationResult"]
        except GraphQLError as exc:
            st.error(str(exc))
            st.stop()

        if result is None:
            st.error(
                f"No verification result was stored for job `{job_id}`. "
                "Check the backend log."
            )
            st.stop()

        st.session_state["result"] = result

    # ---------------- render the stored result ----------------
    result = st.session_state.get("result")
    if not result:
        st.info("Choose an example and a scenario, then press RUN VERIFICATION.")
        return

    st.divider()
    st.header("Job Status")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"**Job ID**\n\n`{result.get('jobId','')}`")
    c2.markdown(f"**Status**\n\n`{result.get('status','')}`")
    c3.markdown(f"**Progress**\n\n{result.get('progress',0)}%")
    st.caption(
        f"Example: `{result.get('example','')}` · "
        f"Scenario: `{result.get('scenario','')}`"
    )
    if result.get("errorMessage"):
        st.warning(result["errorMessage"])

    st.divider()
    render_summary(result.get("simulation"))

    st.divider()
    render_tests(result.get("tests") or [])

    failures = result.get("failures") or []
    if failures:
        st.divider()
        render_failures(failures)

        st.divider()
        render_ai(result.get("aiAnalyses") or [])

    st.divider()
    render_trace(result.get("traceability") or [])

    st.divider()
    render_artifacts(result)


if __name__ == "__main__":
    main()
