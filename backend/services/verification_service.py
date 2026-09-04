"""
Verification service -- the orchestrator.

runVerification flow (background, 4 worker threads):

    1. generate job id
    2. create VerificationJob in Neo4j        QUEUED     progress 0
    3. return the job id immediately
    4. compile with iverilog                  COMPILING  progress 20
    5. simulate with vvp                      SIMULATING progress 50
    6. parse the real simulation.log          PARSING    progress 70
    7. store Simulation/Test/Failure/Waveform in Neo4j
    8. if failures -> ask Groq                ANALYZING  progress 90
    9. store AIAnalysis in Neo4j
   10. mark the job COMPLETED                            progress 100
"""
from __future__ import annotations

import logging
import re
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.config import settings
from backend.models.schemas import (
    FailureInfo,
    JobStatus,
    ParsedLog,
    VerificationResult,
)
from backend.services.ai_service import ai_service
from backend.services.compilation_service import (
    CompilationError,
    compile_design,
)
from backend.services.failure_analyzer import analyze_failures, compilation_failure
from backend.services.log_parser import parse_simulation_log
from backend.services.neo4j_service import neo4j_service
from backend.services.simulation_service import SimulationError, run_simulation

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# the two demo examples
# ---------------------------------------------------------------------
EXAMPLES: Dict[str, Dict[str, str]] = {
    "traffic_light": {
        "label": "Traffic Light Controller",
        "dir": "traffic_light",
        "rtl": "traffic_light.sv",
        "tb": "traffic_light_tb.sv",
    },
    "alu": {
        "label": "4-bit ALU",
        "dir": "alu",
        "rtl": "alu.sv",
        "tb": "alu_tb.sv",
    },
}
SCENARIOS = ("passing", "failing")

_MODULE_RE = re.compile(r"^\s*module\s+([A-Za-z_]\w*)", re.MULTILINE)

# progress checkpoints required by the spec
PROGRESS = {
    JobStatus.QUEUED: 0,
    JobStatus.COMPILING: 20,
    JobStatus.SIMULATING: 50,
    JobStatus.PARSING: 70,
    JobStatus.ANALYZING: 90,
    JobStatus.COMPLETED: 100,
}


class VerificationError(RuntimeError):
    pass


def resolve_paths(example: str, scenario: str) -> Dict[str, Path]:
    """Map (example, scenario) onto real files on disk, validating both."""
    if example not in EXAMPLES:
        raise VerificationError(
            f"Unknown example {example!r}. Choose one of: {', '.join(EXAMPLES)}"
        )
    if scenario not in SCENARIOS:
        raise VerificationError(
            f"Unknown scenario {scenario!r}. Choose one of: {', '.join(SCENARIOS)}"
        )

    meta = EXAMPLES[example]
    base = settings.VERILOG_DIR / meta["dir"] / scenario
    rtl = base / meta["rtl"]
    tb = base / meta["tb"]

    for f in (rtl, tb):
        if not f.is_file():
            raise VerificationError(f"Required SystemVerilog file is missing: {f}")

    return {"rtl": rtl, "testbench": tb, "base": base}


def extract_module_name(rtl_path: Path, default: str = "unknown") -> str:
    try:
        match = _MODULE_RE.search(rtl_path.read_text(encoding="utf-8", errors="replace"))
        return match.group(1) if match else default
    except OSError:
        return default


class VerificationService:
    """Owns the thread pool and the in-memory job mirror."""

    def __init__(self) -> None:
        self._pool = ThreadPoolExecutor(
            max_workers=settings.MAX_WORKERS,
            thread_name_prefix="verify",
        )
        self._lock = threading.Lock()
        # fast mirror of job state so 1s UI polling does not hammer AuraDB;
        # Neo4j remains the system of record.
        self._jobs: Dict[str, VerificationResult] = {}

    # ---------------------------------------------------------------- public
    def shutdown(self) -> None:
        self._pool.shutdown(wait=False, cancel_futures=True)

    def submit(
        self, project_id: str, example: str, scenario: str
    ) -> VerificationResult:
        """Create the job, hand it to a worker, and return immediately."""
        example = (example or "").strip().lower()
        scenario = (scenario or "").strip().lower()

        # validate before we promise the caller a job
        paths = resolve_paths(example, scenario)

        job_id = f"JOB-{uuid.uuid4().hex[:12]}"
        result = VerificationResult(
            job_id=job_id,
            project_id=project_id,
            example=example,
            scenario=scenario,
            status=JobStatus.QUEUED,
            progress=PROGRESS[JobStatus.QUEUED],
            rtl_file=str(paths["rtl"]),
            testbench_file=str(paths["testbench"]),
        )
        with self._lock:
            self._jobs[job_id] = result

        # step 2: create the job node (non-fatal if AuraDB hiccups)
        try:
            neo4j_service.create_job(
                job_id=job_id,
                project_id=project_id,
                example=example,
                scenario=scenario,
                status=JobStatus.QUEUED.value,
                progress=0,
            )
        except Exception as exc:
            log.error("Could not create job node in Neo4j: %s", exc)
            self._note_error(job_id, f"Neo4j unavailable when creating job: {exc}")

        # step 3/4: run the rest in the background
        self._pool.submit(self._run_job, job_id, project_id, example, scenario, paths)
        return result

    def get_job(self, job_id: str) -> Optional[VerificationResult]:
        with self._lock:
            cached = self._jobs.get(job_id)
        if cached is not None:
            return cached
        # not in this process' memory -- fall back to the graph
        try:
            row = neo4j_service.get_job(job_id)
        except Exception as exc:
            log.error("Neo4j job lookup failed: %s", exc)
            return None
        if not row:
            return None
        return VerificationResult(
            job_id=row["jobId"],
            project_id="",
            example=row.get("example") or "",
            scenario=row.get("scenario") or "",
            status=JobStatus(row.get("status") or "QUEUED"),
            progress=int(row.get("progress") or 0),
            error_message=row.get("errorMessage"),
        )

    def get_cached_result(self, job_id: str) -> Optional[VerificationResult]:
        with self._lock:
            return self._jobs.get(job_id)

    # ---------------------------------------------------------------- worker
    def _run_job(
        self,
        job_id: str,
        project_id: str,
        example: str,
        scenario: str,
        paths: Dict[str, Path],
    ) -> None:
        work_dir = settings.JOBS_DIR / job_id
        rtl_path: Path = paths["rtl"]
        tb_path: Path = paths["testbench"]

        try:
            work_dir.mkdir(parents=True, exist_ok=True)

            # ---- register the sources in the graph ----
            rtl_id = f"RTL-{example}-{scenario}"
            tb_id = f"TB-{example}-{scenario}"
            module_name = extract_module_name(rtl_path, default=example)
            self._safe_neo4j(
                job_id,
                lambda: (
                    neo4j_service.upsert_rtl_module(
                        project_id, rtl_id, module_name,
                        rtl_path.name, str(rtl_path),
                    ),
                    neo4j_service.upsert_testbench(
                        project_id, tb_id, tb_path.name, str(tb_path),
                    ),
                    neo4j_service.link_job_sources(job_id, rtl_id, tb_id),
                ),
                "registering RTL/testbench",
            )

            # ======================= COMPILING =======================
            self._set_status(job_id, JobStatus.COMPILING)
            compilation = compile_design(rtl_path, tb_path, work_dir)

            if not compilation.success:
                self._handle_compilation_failure(
                    job_id, project_id, example, scenario, compilation
                )
                return

            # ======================= SIMULATING ======================
            self._set_status(job_id, JobStatus.SIMULATING)
            simulation = run_simulation(Path(compilation.vvp_path), work_dir)

            # ======================= PARSING =========================
            self._set_status(job_id, JobStatus.PARSING)
            combined_log = simulation.stdout
            if simulation.stderr.strip():
                combined_log = f"{combined_log}\n--- stderr ---\n{simulation.stderr}"

            parsed: ParsedLog = parse_simulation_log(combined_log)

            if parsed.total_tests == 0:
                # the simulation ran but printed nothing parsable
                self._fail_job(
                    job_id,
                    simulation.error_message
                    or "Simulation produced no TEST_n lines to parse. "
                       "Check simulation.log in the job directory.",
                    simulation_log=combined_log,
                )
                return

            failures: List[FailureInfo] = analyze_failures(parsed, combined_log)

            # ---- persist Simulation / Test / Failure / Waveform ----
            simulation_id = f"SIM-{uuid.uuid4().hex[:12]}"
            total_duration = round(
                compilation.duration_seconds + simulation.duration_seconds, 4
            )

            def _store_results() -> None:
                neo4j_service.create_simulation(
                    job_id, simulation_id, parsed, total_duration
                )
                # every test, passed AND failed
                neo4j_service.add_tests(simulation_id, parsed.tests)
                neo4j_service.add_failures(simulation_id, failures)
                if simulation.vcd_path:
                    neo4j_service.add_waveform(
                        simulation_id,
                        f"WAVE-{uuid.uuid4().hex[:12]}",
                        Path(simulation.vcd_path).name,
                        simulation.vcd_path,
                    )

            self._safe_neo4j(job_id, _store_results, "storing simulation results")

            # update the in-memory mirror
            self._update(
                job_id,
                simulation_id=simulation_id,
                total_tests=parsed.total_tests,
                passed_tests=parsed.passed_tests,
                failed_tests=parsed.failed_tests,
                simulation_status=parsed.status.value,
                duration_seconds=total_duration,
                tests=parsed.tests,
                failures=failures,
                waveform_path=simulation.vcd_path or "",
                log_path=simulation.log_path or "",
                simulation_log=combined_log,
            )

            if parsed.summary_mismatch:
                self._note_error(
                    job_id, f"Log summary inconsistency: {parsed.summary_mismatch}"
                )
            if not simulation.vcd_path:
                self._note_error(
                    job_id,
                    "Simulation completed but no waveform.vcd was produced "
                    "(check $dumpfile/$dumpvars in the testbench).",
                )

            # ======================= ANALYZING =======================
            # Groq is called ONLY when the simulator found a failure.
            if failures:
                self._set_status(job_id, JobStatus.ANALYZING)
                analyses = []
                for failure in failures:
                    analysis = ai_service.analyze_failure(
                        example=example,
                        scenario=scenario,
                        rtl_path=str(rtl_path),
                        testbench_path=str(tb_path),
                        parsed=parsed,
                        failure=failure,
                        simulation_log=combined_log,
                    )
                    analyses.append(analysis)
                    self._safe_neo4j(
                        job_id,
                        lambda f=failure, a=analysis: neo4j_service.add_ai_analysis(
                            f.failure_id, f"AI-{uuid.uuid4().hex[:12]}", a
                        ),
                        "storing AI analysis",
                    )
                self._update(job_id, ai_analyses=analyses)

            # ======================= COMPLETED =======================
            self._set_status(job_id, JobStatus.COMPLETED, completed=True)
            log.info(
                "Job %s finished: %s (%d/%d passed)",
                job_id, parsed.status.value, parsed.passed_tests, parsed.total_tests,
            )

        except (CompilationError, SimulationError, VerificationError) as exc:
            self._fail_job(job_id, str(exc))
        except Exception as exc:                                # pragma: no cover
            log.exception("Unexpected error in job %s", job_id)
            self._fail_job(job_id, f"Unexpected {type(exc).__name__}: {exc}")

    # -------------------------------------------------------- compile failure
    def _handle_compilation_failure(
        self, job_id, project_id, example, scenario, compilation
    ) -> None:
        failure = compilation_failure(
            compilation.stderr, compilation.error_message
        )
        simulation_id = f"SIM-{uuid.uuid4().hex[:12]}"
        empty = ParsedLog()

        def _store() -> None:
            neo4j_service.create_simulation(
                job_id, simulation_id, empty, compilation.duration_seconds
            )
            neo4j_service.add_failures(simulation_id, [failure])

        self._safe_neo4j(job_id, _store, "storing compilation failure")

        self._update(
            job_id,
            simulation_id=simulation_id,
            simulation_status="FAILED",
            failures=[failure],
            duration_seconds=compilation.duration_seconds,
            simulation_log=compilation.stderr or compilation.stdout,
        )
        self._fail_job(
            job_id,
            compilation.error_message or "iverilog compilation failed",
        )

    # ---------------------------------------------------------------- helpers
    def _set_status(
        self, job_id: str, status: JobStatus, completed: bool = False
    ) -> None:
        progress = PROGRESS.get(status, 0)
        self._update(job_id, status=status, progress=progress)
        self._safe_neo4j(
            job_id,
            lambda: neo4j_service.update_job_status(
                job_id, status.value, progress, completed=completed
            ),
            f"updating job status to {status.value}",
            record_error=False,
        )

    def _fail_job(
        self, job_id: str, message: str, simulation_log: str = ""
    ) -> None:
        fields: Dict[str, Any] = {
            "status": JobStatus.FAILED,
            "progress": 100,
            "error_message": message,
        }
        if simulation_log:
            fields["simulation_log"] = simulation_log
        self._update(job_id, **fields)
        self._safe_neo4j(
            job_id,
            lambda: neo4j_service.update_job_status(
                job_id, JobStatus.FAILED.value, 100,
                error_message=message, completed=True,
            ),
            "marking job FAILED",
            record_error=False,
        )
        log.error("Job %s FAILED: %s", job_id, message)

    def _update(self, job_id: str, **fields) -> None:
        with self._lock:
            current = self._jobs.get(job_id)
            if current is None:
                return
            self._jobs[job_id] = current.model_copy(update=fields)

    def _note_error(self, job_id: str, message: str) -> None:
        """Append a non-fatal warning to the job's error message."""
        with self._lock:
            current = self._jobs.get(job_id)
            if current is None:
                return
            existing = current.error_message
            merged = f"{existing} | {message}" if existing else message
            self._jobs[job_id] = current.model_copy(
                update={"error_message": merged}
            )

    def _safe_neo4j(
        self, job_id: str, fn, what: str, record_error: bool = True
    ) -> bool:
        """
        Run a Neo4j write without letting a database hiccup kill the
        verification run. The problem is surfaced on the job instead.
        """
        try:
            fn()
            return True
        except Exception as exc:
            msg = f"Neo4j error while {what}: {type(exc).__name__}: {exc}"
            log.error("[%s] %s", job_id, msg)
            if record_error:
                self._note_error(job_id, msg)
            return False


verification_service = VerificationService()
