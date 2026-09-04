"""
Failure analyzer -- deterministic, rule-based categorisation of failures.

This runs BEFORE the AI and is completely independent of it. Groq never
decides what category or severity a failure has; it only writes the
human explanation afterwards.

Categories:
    COMPILATION_ERROR   iverilog refused to build the design
    ASSERTION_FAILURE   the simulator itself raised $error/$fatal/assert
    COUNTER_ERROR       an FSM reached a state too early/late -> timing
    FSM_ERROR           an FSM was in a wrong state, not timing related
    OUTPUT_MISMATCH     a datapath produced the wrong value
    UNKNOWN             nothing above matched

Severity: LOW / MEDIUM / HIGH / CRITICAL
"""
from __future__ import annotations

import re
import uuid
from typing import List, Optional

from backend.models.schemas import (
    FailureCategory,
    FailureInfo,
    ParsedLog,
    Severity,
    TestResult,
)

# ---------------------------------------------------------------------
# evidence detectors
# ---------------------------------------------------------------------

# a value that is purely a number (decimal / hex / binary)
_NUMERIC_RE = re.compile(r"^[+-]?(0[xXbB])?[0-9a-fA-F_]+$")

# a value that looks like an FSM state label, e.g. A_GREEN, B_YELLOW, IDLE
_STATE_RE = re.compile(
    r"\b(A_GREEN|A_YELLOW|B_GREEN|B_YELLOW|IDLE|S_[A-Z0-9_]+|[A-Z]+_(GREEN|YELLOW|RED))\b"
)

# wording that proves the check was about *when* something happened
_TIMING_WORDS = (
    "cycle", "cycles", "counter", "count", "dwell", "tick", "ticks",
    "duration", "timing", "too early", "too late", "after", "period",
)

_ASSERTION_RE = re.compile(
    r"(assertion (failed|error)|\$error|\$fatal|\berror\b.*\bassert)", re.IGNORECASE
)


def _is_numeric(value: str) -> bool:
    v = (value or "").strip()
    return bool(v) and bool(_NUMERIC_RE.match(v))


def _is_state(value: str) -> bool:
    return bool(_STATE_RE.search((value or "").upper()))


def _mentions_timing(*texts: str) -> bool:
    blob = " ".join(t or "" for t in texts).lower()
    return any(w in blob for w in _TIMING_WORDS)


# ---------------------------------------------------------------------
# categorisation
# ---------------------------------------------------------------------
def categorize_test_failure(test: TestResult, log_text: str = "") -> FailureCategory:
    """Deterministically decide the category of a single failed test."""
    expected = (test.expected or "").strip()
    actual = (test.actual or "").strip()

    # 1. the simulator raised an assertion for this very test
    if _ASSERTION_RE.search(test.message or ""):
        return FailureCategory.ASSERTION_FAILURE

    # 2. FSM state comparison
    if _is_state(expected) and _is_state(actual):
        # The FSM was in a *different legal state* and the check talks
        # about cycles/dwell/counters -> the dwell counter is wrong.
        if _mentions_timing(test.name, test.message):
            return FailureCategory.COUNTER_ERROR
        return FailureCategory.FSM_ERROR

    # 3. plain value comparison -> datapath produced a wrong number
    if _is_numeric(expected) and _is_numeric(actual):
        return FailureCategory.OUTPUT_MISMATCH

    # 4. we have both values but cannot classify them any further
    if expected and actual:
        return FailureCategory.OUTPUT_MISMATCH

    return FailureCategory.UNKNOWN


def assign_severity(
    category: FailureCategory,
    failed_tests: int = 1,
    total_tests: int = 1,
) -> Severity:
    """Deterministic severity from the category plus how much broke."""
    if category == FailureCategory.COMPILATION_ERROR:
        return Severity.CRITICAL

    ratio = (failed_tests / total_tests) if total_tests else 1.0

    if category in (FailureCategory.COUNTER_ERROR, FailureCategory.FSM_ERROR):
        # control-path bugs are always serious; everything broken is critical
        return Severity.CRITICAL if ratio >= 1.0 else Severity.HIGH

    if category == FailureCategory.ASSERTION_FAILURE:
        return Severity.HIGH

    if category == FailureCategory.OUTPUT_MISMATCH:
        # a datapath bug that hits most of the tests is a bigger deal
        return Severity.HIGH if ratio > 0.5 else Severity.MEDIUM

    return Severity.MEDIUM if failed_tests else Severity.LOW


def analyze_failures(parsed: ParsedLog, log_text: str = "") -> List[FailureInfo]:
    """Build one :class:`FailureInfo` per failed test in the parsed log."""
    failures: List[FailureInfo] = []
    failed = parsed.failed

    for test in failed:
        category = categorize_test_failure(test, log_text)
        severity = assign_severity(category, len(failed), parsed.total_tests or 1)
        failures.append(
            FailureInfo(
                failure_id=f"FAIL-{uuid.uuid4().hex[:10]}",
                category=category,
                severity=severity,
                expected=test.expected,
                actual=test.actual,
                message=test.message or (
                    f"{test.name or test.test_id}: expected "
                    f"{test.expected!r} but got {test.actual!r}"
                ),
                test_id=test.test_id,
                test_name=test.name,
            )
        )
    return failures


def compilation_failure(stderr: str, message: Optional[str] = None) -> FailureInfo:
    """A dedicated FailureInfo for a design that would not even compile."""
    text = (message or stderr or "iverilog compilation failed").strip()
    return FailureInfo(
        failure_id=f"FAIL-{uuid.uuid4().hex[:10]}",
        category=FailureCategory.COMPILATION_ERROR,
        severity=Severity.CRITICAL,
        expected="clean compilation",
        actual="compilation error",
        message=text[:2000],
        test_id="COMPILE",
        test_name="Compilation",
    )
