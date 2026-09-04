"""
Log parser -- turns the *real* Icarus Verilog simulation output into
structured Pydantic models.

Contract with the testbenches (see verilog/**/*_tb.sv):

    TEST_<n>: PASS|FAIL
    NAME: <test name>
    EXPECTED: <value>
    ACTUAL: <value>
    MESSAGE: <human readable note>
    ...
    TOTAL_TESTS: <n>
    PASSED: <n>
    FAILED: <n>
    STATUS: PASSED|FAILED

Design rules:
  * The simulator is the SOURCE OF TRUTH. Nothing here invents a result.
  * The overall status is never hard-coded in Python -- it is read from
    the `STATUS:` line the testbench printed, and cross-checked against
    the per-test lines. A disagreement is reported, not hidden.
"""
from __future__ import annotations

import re
from typing import List, Optional

from backend.models.schemas import (
    OverallStatus,
    ParsedLog,
    TestResult,
    TestStatus,
)

# ---------------------------------------------------------------------
# line patterns
# ---------------------------------------------------------------------
_TEST_RE = re.compile(r"^\s*TEST[_\s-]*(\d+)\s*:\s*(PASS|FAIL)\s*$", re.IGNORECASE)
_NAME_RE = re.compile(r"^\s*NAME\s*:\s*(.*)$", re.IGNORECASE)
_EXPECTED_RE = re.compile(r"^\s*EXPECTED\s*:\s*(.*)$", re.IGNORECASE)
_ACTUAL_RE = re.compile(r"^\s*ACTUAL\s*:\s*(.*)$", re.IGNORECASE)
_MESSAGE_RE = re.compile(r"^\s*MESSAGE\s*:\s*(.*)$", re.IGNORECASE)

_TOTAL_RE = re.compile(r"^\s*TOTAL[_\s-]*TESTS\s*:\s*(\d+)\s*$", re.IGNORECASE)
_PASSED_RE = re.compile(r"^\s*PASSED\s*:\s*(\d+)\s*$", re.IGNORECASE)
_FAILED_RE = re.compile(r"^\s*FAILED\s*:\s*(\d+)\s*$", re.IGNORECASE)
_STATUS_RE = re.compile(r"^\s*STATUS\s*:\s*(PASSED|FAILED)\s*$", re.IGNORECASE)

# things Icarus Verilog itself prints when the testbench misbehaves
_SV_ASSERT_RE = re.compile(r"(assertion (failed|error)|\$error|\$fatal)", re.IGNORECASE)


def parse_simulation_log(log_text: str) -> ParsedLog:
    """Parse raw simulator stdout(+stderr) into a :class:`ParsedLog`."""
    if log_text is None:
        log_text = ""

    tests: List[TestResult] = []
    current: Optional[TestResult] = None

    reported_total: Optional[int] = None
    reported_passed: Optional[int] = None
    reported_failed: Optional[int] = None
    reported_status: Optional[OverallStatus] = None

    for raw_line in log_text.splitlines():
        # ---- start of a new TEST_n block ----
        m = _TEST_RE.match(raw_line)
        if m:
            number = int(m.group(1))
            current = TestResult(
                test_id=f"TEST_{number}",
                test_number=number,
                status=TestStatus(m.group(2).upper()),
            )
            tests.append(current)
            continue

        # ---- summary lines (must be checked before the per-test
        #      attribute lines, because PASSED/FAILED look similar) ----
        m = _TOTAL_RE.match(raw_line)
        if m:
            reported_total = int(m.group(1))
            current = None          # summary block closes the last test
            continue

        m = _PASSED_RE.match(raw_line)
        if m:
            reported_passed = int(m.group(1))
            current = None
            continue

        m = _FAILED_RE.match(raw_line)
        if m:
            reported_failed = int(m.group(1))
            current = None
            continue

        m = _STATUS_RE.match(raw_line)
        if m:
            reported_status = OverallStatus(m.group(1).upper())
            current = None
            continue

        # ---- attributes of the test block we are inside ----
        if current is not None:
            m = _NAME_RE.match(raw_line)
            if m:
                current.name = m.group(1).strip()
                continue
            m = _EXPECTED_RE.match(raw_line)
            if m:
                current.expected = m.group(1).strip()
                continue
            m = _ACTUAL_RE.match(raw_line)
            if m:
                current.actual = m.group(1).strip()
                continue
            m = _MESSAGE_RE.match(raw_line)
            if m:
                current.message = m.group(1).strip()
                continue

    # -----------------------------------------------------------------
    # Counts derived from the per-test lines the simulator printed.
    # -----------------------------------------------------------------
    derived_total = len(tests)
    derived_passed = sum(1 for t in tests if t.status == TestStatus.PASS)
    derived_failed = sum(1 for t in tests if t.status == TestStatus.FAIL)

    summary_derived = reported_status is None and reported_total is None
    mismatch_notes: List[str] = []

    total = reported_total if reported_total is not None else derived_total
    passed = reported_passed if reported_passed is not None else derived_passed
    failed = reported_failed if reported_failed is not None else derived_failed

    if reported_total is not None and reported_total != derived_total:
        mismatch_notes.append(
            f"testbench reported TOTAL_TESTS={reported_total} "
            f"but printed {derived_total} TEST_n lines"
        )
    if reported_passed is not None and reported_passed != derived_passed:
        mismatch_notes.append(
            f"testbench reported PASSED={reported_passed} "
            f"but printed {derived_passed} PASS lines"
        )
    if reported_failed is not None and reported_failed != derived_failed:
        mismatch_notes.append(
            f"testbench reported FAILED={reported_failed} "
            f"but printed {derived_failed} FAIL lines"
        )

    if reported_status is not None:
        status = reported_status
    else:
        # No STATUS line: fall back to what the per-test lines say.
        status = OverallStatus.FAILED if derived_failed else OverallStatus.PASSED

    # A STATUS line that contradicts the per-test lines is a real problem:
    # trust the failing evidence, and say so.
    if reported_status == OverallStatus.PASSED and derived_failed > 0:
        mismatch_notes.append(
            f"testbench reported STATUS: PASSED but {derived_failed} "
            f"TEST_n line(s) say FAIL -- treating the run as FAILED"
        )
        status = OverallStatus.FAILED

    # An assertion/$error/$fatal from the simulator with no tests at all
    # still counts as a failed run.
    if derived_total == 0 and _SV_ASSERT_RE.search(log_text):
        status = OverallStatus.FAILED

    return ParsedLog(
        tests=tests,
        total_tests=total,
        passed_tests=passed,
        failed_tests=failed,
        status=status,
        summary_mismatch="; ".join(mismatch_notes) if mismatch_notes else None,
        summary_derived=summary_derived,
    )


def parse_simulation_log_file(path: str) -> ParsedLog:
    """Convenience wrapper: read `simulation.log` from disk and parse it."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return parse_simulation_log(fh.read())
