"""
Pydantic models shared by every service.

These are the *internal* contract of the platform. The GraphQL layer
(`backend/graphql/types.py`) mirrors them for the wire format.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# =====================================================================
# Enumerations
# =====================================================================
class TestStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


class OverallStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    COMPILING = "COMPILING"
    SIMULATING = "SIMULATING"
    PARSING = "PARSING"
    ANALYZING = "ANALYZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class FailureCategory(str, Enum):
    COUNTER_ERROR = "COUNTER_ERROR"
    FSM_ERROR = "FSM_ERROR"
    OUTPUT_MISMATCH = "OUTPUT_MISMATCH"
    ASSERTION_FAILURE = "ASSERTION_FAILURE"
    COMPILATION_ERROR = "COMPILATION_ERROR"
    UNKNOWN = "UNKNOWN"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# =====================================================================
# Log parsing
# =====================================================================
class TestResult(BaseModel):
    """One TEST_n block scraped out of the real simulator output."""

    test_id: str
    test_number: int
    name: str = ""
    status: TestStatus
    expected: str = ""
    actual: str = ""
    message: str = ""


class ParsedLog(BaseModel):
    """
    Structured view of `simulation.log`.

    The simulator/testbench is the source of truth: every field here is
    derived from text the simulator actually printed.
    """

    tests: List[TestResult] = Field(default_factory=list)
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    status: OverallStatus = OverallStatus.PASSED

    # set when the summary the testbench printed disagrees with the
    # per-test lines -- surfaced instead of silently ignored
    summary_mismatch: Optional[str] = None
    # True when the testbench printed no TOTAL_TESTS/STATUS summary at all
    summary_derived: bool = False

    @property
    def failed(self) -> List[TestResult]:
        return [t for t in self.tests if t.status == TestStatus.FAIL]

    @property
    def passed(self) -> List[TestResult]:
        return [t for t in self.tests if t.status == TestStatus.PASS]


# =====================================================================
# Failure analysis
# =====================================================================
class FailureInfo(BaseModel):
    failure_id: str = ""
    category: FailureCategory = FailureCategory.UNKNOWN
    severity: Severity = Severity.MEDIUM
    expected: str = ""
    actual: str = ""
    message: str = ""
    test_id: str = ""
    test_name: str = ""


# =====================================================================
# Subprocess results
# =====================================================================
class CompilationResult(BaseModel):
    success: bool
    command: List[str] = Field(default_factory=list)
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    duration_seconds: float = 0.0
    vvp_path: Optional[str] = None
    error_message: Optional[str] = None


class SimulationRun(BaseModel):
    success: bool
    command: List[str] = Field(default_factory=list)
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    duration_seconds: float = 0.0
    log_path: Optional[str] = None
    vcd_path: Optional[str] = None
    error_message: Optional[str] = None
    timed_out: bool = False


# =====================================================================
# Groq AI analysis
# =====================================================================
class AIAnalysis(BaseModel):
    """
    Validated Groq response.

    The AI only ever *explains* a failure the simulator already found; it
    never decides PASS/FAIL and never invents test results.
    """

    rootCause: str = Field(min_length=1)
    explanation: str = Field(min_length=1)
    recommendation: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("rootCause", "explanation", "recommendation", mode="before")
    @classmethod
    def _stringify(cls, v):
        if v is None:
            return ""
        if isinstance(v, (list, tuple)):
            return " ".join(str(x) for x in v)
        return str(v).strip()

    @field_validator("confidence", mode="before")
    @classmethod
    def _coerce_confidence(cls, v):
        """Accept 0.95, "0.95" or 95 (percent) and clamp into [0, 1]."""
        if v is None:
            return 0.5
        try:
            f = float(v)
        except (TypeError, ValueError):
            return 0.5
        if f > 1.0:
            f = f / 100.0
        return max(0.0, min(1.0, f))


# =====================================================================
# Aggregate result handed back over GraphQL
# =====================================================================
class VerificationResult(BaseModel):
    job_id: str
    project_id: str
    example: str
    scenario: str
    status: JobStatus
    progress: int = 0
    error_message: Optional[str] = None

    rtl_file: str = ""
    testbench_file: str = ""

    simulation_id: str = ""
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    simulation_status: str = ""
    duration_seconds: float = 0.0

    tests: List[TestResult] = Field(default_factory=list)
    failures: List[FailureInfo] = Field(default_factory=list)
    ai_analyses: List[AIAnalysis] = Field(default_factory=list)

    waveform_path: str = ""
    log_path: str = ""
    simulation_log: str = ""
