"""Tests for the simulation log parser."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.models.schemas import OverallStatus, TestStatus  # noqa: E402
from backend.services.log_parser import parse_simulation_log  # noqa: E402

# ---------------------------------------------------------------------
# Real captured output from `vvp` for verilog/traffic_light/passing
# ---------------------------------------------------------------------
PASSING_TRAFFIC_LIGHT_LOG = """\
VCD info: dumpfile waveform.vcd opened for output.
========================================
TRAFFIC LIGHT CONTROLLER VERIFICATION
========================================

TEST_1: PASS
NAME: Reset
EXPECTED: A_GREEN/0
ACTUAL: A_GREEN/0
MESSAGE: Asserting rst_n must force the FSM to A_GREEN with the dwell counter cleared

TEST_2: PASS
NAME: A_GREEN
EXPECTED: A_GREEN
ACTUAL: A_GREEN
MESSAGE: One cycle after reset release the FSM must still be dwelling in A_GREEN

TEST_3: PASS
NAME: A_YELLOW
EXPECTED: A_YELLOW
ACTUAL: A_YELLOW
MESSAGE: A_GREEN must dwell for 4 cycles, so cycle 4 must be A_YELLOW

TEST_4: PASS
NAME: B_GREEN
EXPECTED: B_GREEN
ACTUAL: B_GREEN
MESSAGE: A_YELLOW must dwell for 2 cycles, so cycle 6 must be B_GREEN

========================================
TOTAL_TESTS: 4
PASSED: 4
FAILED: 0
STATUS: PASSED
========================================
"""

# ---------------------------------------------------------------------
# Real captured output for verilog/traffic_light/failing
# ---------------------------------------------------------------------
FAILING_TRAFFIC_LIGHT_LOG = """\
VCD info: dumpfile waveform.vcd opened for output.
TEST_1: PASS
NAME: Reset
EXPECTED: A_GREEN/0
ACTUAL: A_GREEN/0
MESSAGE: Asserting rst_n must force the FSM to A_GREEN with the dwell counter cleared

TEST_2: PASS
NAME: A_GREEN
EXPECTED: A_GREEN
ACTUAL: A_GREEN
MESSAGE: One cycle after reset release the FSM must still be dwelling in A_GREEN

TEST_3: FAIL
NAME: A_YELLOW
EXPECTED: A_YELLOW
ACTUAL: B_GREEN
MESSAGE: A_GREEN must dwell for 4 cycles, so cycle 4 must be A_YELLOW

TEST_4: FAIL
NAME: B_GREEN
EXPECTED: B_GREEN
ACTUAL: B_YELLOW
MESSAGE: A_YELLOW must dwell for 2 cycles, so cycle 6 must be B_GREEN

TOTAL_TESTS: 4
PASSED: 2
FAILED: 2
STATUS: FAILED
"""

FAILING_ALU_LOG = """\
TEST_1: PASS
NAME: ADD
EXPECTED: 8
ACTUAL: 8
MESSAGE: opcode=ADD A=5 B=3 -> result[3:0] must be 8

TEST_2: PASS
NAME: SUB
EXPECTED: 5
ACTUAL: 5
MESSAGE: opcode=SUB A=7 B=2 -> result[3:0] must be 5

TEST_3: PASS
NAME: AND
EXPECTED: 2
ACTUAL: 2
MESSAGE: opcode=AND A=6 B=3 -> result[3:0] must be 2

TEST_4: FAIL
NAME: OR
EXPECTED: 7
ACTUAL: 2
MESSAGE: opcode=OR A=6 B=3 -> result[3:0] must be 7

TOTAL_TESTS: 4
PASSED: 3
FAILED: 1
STATUS: FAILED
"""


# =====================================================================
# 1. passing log parsing
# =====================================================================
def test_parse_passing_traffic_light():
    parsed = parse_simulation_log(PASSING_TRAFFIC_LIGHT_LOG)

    assert parsed.total_tests == 4
    assert parsed.passed_tests == 4
    assert parsed.failed_tests == 0
    assert parsed.status is OverallStatus.PASSED
    assert parsed.summary_mismatch is None
    assert parsed.summary_derived is False

    assert [t.test_id for t in parsed.tests] == [
        "TEST_1", "TEST_2", "TEST_3", "TEST_4"
    ]
    assert [t.name for t in parsed.tests] == [
        "Reset", "A_GREEN", "A_YELLOW", "B_GREEN"
    ]
    assert all(t.status is TestStatus.PASS for t in parsed.tests)
    assert parsed.failed == []


def test_passing_log_dict_shape():
    parsed = parse_simulation_log(PASSING_TRAFFIC_LIGHT_LOG)
    assert {
        "total_tests": parsed.total_tests,
        "passed_tests": parsed.passed_tests,
        "failed_tests": parsed.failed_tests,
        "status": parsed.status.value,
    } == {
        "total_tests": 4,
        "passed_tests": 4,
        "failed_tests": 0,
        "status": "PASSED",
    }


# =====================================================================
# 2. failing log parsing
# =====================================================================
def test_parse_failing_traffic_light():
    parsed = parse_simulation_log(FAILING_TRAFFIC_LIGHT_LOG)

    assert parsed.total_tests == 4
    assert parsed.passed_tests == 2
    assert parsed.failed_tests == 2
    assert parsed.status is OverallStatus.FAILED

    # passed tests are still present -- nothing is hidden
    assert len(parsed.passed) == 2
    assert len(parsed.failed) == 2

    third = parsed.tests[2]
    assert third.test_id == "TEST_3"
    assert third.name == "A_YELLOW"
    assert third.status is TestStatus.FAIL
    assert third.expected == "A_YELLOW"
    assert third.actual == "B_GREEN"


def test_failing_log_dict_shape():
    parsed = parse_simulation_log(FAILING_TRAFFIC_LIGHT_LOG)
    assert {
        "total_tests": parsed.total_tests,
        "passed_tests": parsed.passed_tests,
        "failed_tests": parsed.failed_tests,
        "status": parsed.status.value,
    } == {
        "total_tests": 4,
        "passed_tests": 2,
        "failed_tests": 2,
        "status": "FAILED",
    }


def test_parse_failing_alu():
    parsed = parse_simulation_log(FAILING_ALU_LOG)
    assert (parsed.total_tests, parsed.passed_tests, parsed.failed_tests) == (4, 3, 1)
    assert parsed.status is OverallStatus.FAILED
    failed = parsed.failed[0]
    assert failed.name == "OR"
    assert failed.expected == "7"
    assert failed.actual == "2"


# =====================================================================
# robustness
# =====================================================================
def test_empty_log_is_not_a_pass_by_accident():
    parsed = parse_simulation_log("")
    assert parsed.total_tests == 0
    assert parsed.tests == []


def test_status_is_derived_when_testbench_prints_no_summary():
    parsed = parse_simulation_log("TEST_1: PASS\nTEST_2: FAIL\n")
    assert parsed.summary_derived is True
    assert parsed.total_tests == 2
    assert parsed.failed_tests == 1
    assert parsed.status is OverallStatus.FAILED


def test_failing_evidence_overrides_a_lying_status_line():
    """A STATUS: PASSED line cannot mask a FAIL test line."""
    parsed = parse_simulation_log(
        "TEST_1: FAIL\nEXPECTED: 7\nACTUAL: 2\n"
        "TOTAL_TESTS: 1\nPASSED: 1\nFAILED: 0\nSTATUS: PASSED\n"
    )
    assert parsed.status is OverallStatus.FAILED
    assert parsed.summary_mismatch is not None
    assert "PASSED" in parsed.summary_mismatch


def test_summary_mismatch_is_reported():
    parsed = parse_simulation_log(
        "TEST_1: PASS\nTEST_2: PASS\n"
        "TOTAL_TESTS: 5\nPASSED: 2\nFAILED: 0\nSTATUS: PASSED\n"
    )
    assert parsed.summary_mismatch is not None
    assert "TOTAL_TESTS=5" in parsed.summary_mismatch


@pytest.mark.parametrize(
    "line,expected_id",
    [("TEST_1: PASS", "TEST_1"), ("test_7: pass", "TEST_7"), ("  TEST 3 : FAIL  ", "TEST_3")],
)
def test_test_line_variants(line, expected_id):
    parsed = parse_simulation_log(line)
    assert parsed.tests[0].test_id == expected_id
