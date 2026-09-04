"""
GraphQL queries.

Reads come from Neo4j (the system of record). While a job is still
running the in-memory mirror in `verification_service` fills the gaps so
the UI can poll for progress without waiting on a write to land.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import strawberry

from backend.config import settings
from backend.database.neo4j_client import neo4j_client
from backend.graphql.types import (
    AIAnalysisType,
    FailureType,
    HealthType,
    ProjectType,
    RTLModuleType,
    SimulationType,
    TestType,
    TestbenchType,
    TraceStepType,
    VerificationJobType,
    VerificationResultType,
    WaveformType,
)
from backend.models.schemas import VerificationResult
from backend.services.compilation_service import iverilog_version
from backend.services.neo4j_service import neo4j_service
from backend.services.verification_service import verification_service

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# helpers: Neo4j row -> GraphQL type
# ---------------------------------------------------------------------
def _test_sort_key(t: Dict[str, Any]):
    return (t.get("number") if t.get("number") is not None else 0, t.get("testId") or "")


def _short_test_id(test_id: str) -> str:
    """`SIM-abc:TEST_3` -> `TEST_3`."""
    return test_id.split(":")[-1] if test_id else ""


def _build_traceability(row: Dict[str, Any]) -> List[TraceStepType]:
    """
    Project -> RTL -> Testbench -> Job -> Simulation -> Test -> Failure -> AI
    """
    failures = row.get("failures") or []
    analyses = row.get("aiAnalyses") or []
    tests = row.get("tests") or []

    first_failure = failures[0] if failures else None
    first_analysis = analyses[0] if analyses else None

    if first_failure:
        test_desc = f"{first_failure.get('testName') or ''} — FAIL"
    elif tests:
        test_desc = f"{len(tests)} test(s) — all PASS"
    else:
        test_desc = "no tests recorded"

    steps = [
        ("Project", row.get("projectName") or row.get("projectId") or "—"),
        ("RTL Module", row.get("rtlFileName") or row.get("rtlModuleName") or "—"),
        ("Testbench", row.get("testbenchFileName") or "—"),
        ("Verification Job", row.get("jobId") or "—"),
        (
            "Simulation",
            f"{row.get('simulationId') or '—'} "
            f"({row.get('passedTests') or 0}/{row.get('totalTests') or 0} passed)",
        ),
        ("Test", test_desc),
        (
            "Failure",
            f"{first_failure['category']} / {first_failure['severity']}"
            if first_failure else "none",
        ),
        (
            "AI Analysis",
            (first_analysis.get("rootCause") or "—")
            if first_analysis else "not required (no failures)",
        ),
    ]
    return [
        TraceStepType(level=i + 1, label=label, value=str(value))
        for i, (label, value) in enumerate(steps)
    ]


def _result_from_neo4j(row: Dict[str, Any], cached: Optional[VerificationResult]):
    tests = sorted(row.get("tests") or [], key=_test_sort_key)

    rtl = None
    if row.get("rtlFileName"):
        rtl = RTLModuleType(
            rtlId=row.get("rtlModuleName") or "",
            moduleName=row.get("rtlModuleName") or "",
            fileName=row.get("rtlFileName") or "",
            filePath=row.get("rtlFilePath") or "",
        )
    tb = None
    if row.get("testbenchFileName"):
        tb = TestbenchType(
            testbenchId=row.get("testbenchFileName") or "",
            fileName=row.get("testbenchFileName") or "",
            filePath=row.get("testbenchFilePath") or "",
        )
    sim = None
    if row.get("simulationId"):
        sim = SimulationType(
            simulationId=row["simulationId"],
            status=row.get("simulationStatus") or "",
            totalTests=int(row.get("totalTests") or 0),
            passedTests=int(row.get("passedTests") or 0),
            failedTests=int(row.get("failedTests") or 0),
            duration=float(row.get("duration") or 0.0),
        )
    wave = None
    if row.get("waveformFilePath"):
        wave = WaveformType(
            waveformId=row.get("waveformFileName") or "waveform",
            fileName=row.get("waveformFileName") or "waveform.vcd",
            filePath=row.get("waveformFilePath") or "",
        )

    return VerificationResultType(
        jobId=row.get("jobId") or "",
        projectId=row.get("projectId") or "",
        projectName=row.get("projectName") or "",
        example=row.get("example") or "",
        scenario=row.get("scenario") or "",
        status=row.get("status") or "QUEUED",
        progress=int(row.get("progress") or 0),
        errorMessage=(
            row.get("errorMessage")
            or (cached.error_message if cached else None)
        ),
        rtlModule=rtl,
        testbench=tb,
        simulation=sim,
        waveform=wave,
        tests=[
            TestType(
                testId=_short_test_id(t.get("testId") or ""),
                name=t.get("name") or "",
                status=t.get("status") or "",
                expected=t.get("expected") or "",
                actual=t.get("actual") or "",
                message=t.get("message") or "",
            )
            for t in tests
        ],
        failures=[
            FailureType(
                failureId=f.get("failureId") or "",
                category=f.get("category") or "",
                severity=f.get("severity") or "",
                expected=f.get("expected") or "",
                actual=f.get("actual") or "",
                message=f.get("message") or "",
                testId=f.get("testId") or "",
                testName=f.get("testName") or "",
            )
            for f in (row.get("failures") or [])
        ],
        aiAnalyses=[
            AIAnalysisType(
                analysisId=a.get("analysisId") or "",
                rootCause=a.get("rootCause") or "",
                explanation=a.get("explanation") or "",
                recommendation=a.get("recommendation") or "",
                confidence=float(a.get("confidence") or 0.0),
                createdAt=a.get("createdAt") or "",
            )
            for a in (row.get("aiAnalyses") or [])
        ],
        traceability=_build_traceability(row),
        simulationLog=cached.simulation_log if cached else "",
    )


def _result_from_cache(cached: VerificationResult) -> VerificationResultType:
    """Fallback view built purely from this process' memory."""
    return VerificationResultType(
        jobId=cached.job_id,
        projectId=cached.project_id,
        example=cached.example,
        scenario=cached.scenario,
        status=cached.status.value,
        progress=cached.progress,
        errorMessage=cached.error_message,
        simulation=(
            SimulationType(
                simulationId=cached.simulation_id,
                status=cached.simulation_status,
                totalTests=cached.total_tests,
                passedTests=cached.passed_tests,
                failedTests=cached.failed_tests,
                duration=cached.duration_seconds,
            )
            if cached.simulation_id
            else None
        ),
        tests=[
            TestType(
                testId=t.test_id, name=t.name, status=t.status.value,
                expected=t.expected, actual=t.actual, message=t.message,
            )
            for t in cached.tests
        ],
        failures=[
            FailureType(
                failureId=f.failure_id, category=f.category.value,
                severity=f.severity.value, expected=f.expected,
                actual=f.actual, message=f.message,
                testId=f.test_id, testName=f.test_name,
            )
            for f in cached.failures
        ],
        aiAnalyses=[
            AIAnalysisType(
                analysisId="", rootCause=a.rootCause, explanation=a.explanation,
                recommendation=a.recommendation, confidence=a.confidence,
            )
            for a in cached.ai_analyses
        ],
        waveform=(
            WaveformType(
                waveformId="waveform",
                fileName="waveform.vcd",
                filePath=cached.waveform_path,
            )
            if cached.waveform_path
            else None
        ),
        simulationLog=cached.simulation_log,
    )


# ---------------------------------------------------------------------
# Query root
# ---------------------------------------------------------------------
@strawberry.type
class Query:

    @strawberry.field(description="Service + dependency health.")
    def health(self) -> HealthType:
        neo = neo4j_client.health()
        return HealthType(
            status="ok",
            neo4j=neo,
            groq="configured" if settings.groq_configured else "not configured",
            iverilog=iverilog_version(),
        )

    @strawberry.field(description="All projects stored in Neo4j.")
    def projects(self) -> List[ProjectType]:
        try:
            rows = neo4j_service.list_projects()
        except Exception as exc:
            log.error("projects query failed: %s", exc)
            return []
        return [
            ProjectType(
                projectId=r.get("projectId") or "",
                name=r.get("name") or "",
                description=r.get("description") or "",
                createdAt=r.get("createdAt") or "",
            )
            for r in rows
        ]

    @strawberry.field(description="One project by id.")
    def project(self, projectId: str) -> Optional[ProjectType]:
        try:
            row = neo4j_service.get_project(projectId)
        except Exception as exc:
            log.error("project query failed: %s", exc)
            return None
        if not row:
            return None
        return ProjectType(
            projectId=row.get("projectId") or "",
            name=row.get("name") or "",
            description=row.get("description") or "",
            createdAt=row.get("createdAt") or "",
        )

    @strawberry.field(description="Live status/progress of a verification job.")
    def verificationJob(self, jobId: str) -> Optional[VerificationJobType]:
        cached = verification_service.get_job(jobId)
        if cached is not None:
            return VerificationJobType(
                jobId=cached.job_id,
                status=cached.status.value,
                progress=cached.progress,
                errorMessage=cached.error_message,
                example=cached.example,
                scenario=cached.scenario,
            )
        try:
            row = neo4j_service.get_job(jobId)
        except Exception as exc:
            log.error("verificationJob query failed: %s", exc)
            return None
        if not row:
            return None
        return VerificationJobType(
            jobId=row["jobId"],
            status=row.get("status") or "",
            progress=int(row.get("progress") or 0),
            createdAt=row.get("createdAt") or "",
            completedAt=row.get("completedAt"),
            errorMessage=row.get("errorMessage"),
            example=row.get("example") or "",
            scenario=row.get("scenario") or "",
        )

    @strawberry.field(description="Complete result for a job, read back out of Neo4j.")
    def verificationResult(self, jobId: str) -> Optional[VerificationResultType]:
        cached = verification_service.get_cached_result(jobId)
        try:
            row = neo4j_service.get_verification_result(jobId)
        except Exception as exc:
            log.error("verificationResult query failed: %s", exc)
            row = None

        if row:
            result = _result_from_neo4j(row, cached)
            # while the job is mid-flight the live mirror is fresher
            if cached is not None and cached.status.value not in (
                "COMPLETED", "FAILED"
            ):
                result.status = cached.status.value
                result.progress = cached.progress
            return result

        if cached is not None:
            return _result_from_cache(cached)
        return None

    @strawberry.field(description="Failures, optionally scoped to one job.")
    def failures(self, jobId: Optional[str] = None) -> List[FailureType]:
        try:
            rows = neo4j_service.get_failures(jobId)
        except Exception as exc:
            log.error("failures query failed: %s", exc)
            return []
        return [
            FailureType(
                failureId=r.get("failureId") or "",
                category=r.get("category") or "",
                severity=r.get("severity") or "",
                expected=r.get("expected") or "",
                actual=r.get("actual") or "",
                message=r.get("message") or "",
                testId=r.get("testId") or "",
                testName=r.get("testName") or "",
            )
            for r in rows
        ]

    @strawberry.field(description="AI analyses attached to a job's failures.")
    def aiAnalysis(self, jobId: str) -> List[AIAnalysisType]:
        try:
            rows = neo4j_service.get_ai_analysis(jobId)
        except Exception as exc:
            log.error("aiAnalysis query failed: %s", exc)
            return []
        return [
            AIAnalysisType(
                analysisId=r.get("analysisId") or "",
                rootCause=r.get("rootCause") or "",
                explanation=r.get("explanation") or "",
                recommendation=r.get("recommendation") or "",
                confidence=float(r.get("confidence") or 0.0),
                createdAt=r.get("createdAt") or "",
                failureId=r.get("failureId") or "",
                category=r.get("category") or "",
            )
            for r in rows
        ]

    @strawberry.field(description="Full Project->...->AIAnalysis trace for a job.")
    def traceability(self, jobId: str) -> List[TraceStepType]:
        try:
            row = neo4j_service.get_verification_result(jobId)
        except Exception as exc:
            log.error("traceability query failed: %s", exc)
            return []
        return _build_traceability(row) if row else []
