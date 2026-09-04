"""Tests for the deterministic failure analyzer and the AI response model."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.models.schemas import (  # noqa: E402
    AIAnalysis,
    FailureCategory,
    Severity,
    TestResult,
    TestStatus,
)
from backend.services.failure_analyzer import (  # noqa: E402
    analyze_failures,
    assign_severity,
    categorize_test_failure,
    compilation_failure,
)
from backend.services.log_parser import parse_simulation_log  # noqa: E402

from tests.test_log_parser import (  # noqa: E402
    FAILING_ALU_LOG,
    FAILING_TRAFFIC_LIGHT_LOG,
    PASSING_TRAFFIC_LIGHT_LOG,
)


def _test(name, expected, actual, message=""):
    return TestResult(
        test_id="TEST_3", test_number=3, name=name,
        status=TestStatus.FAIL, expected=expected, actual=actual,
        message=message,
    )


# =====================================================================
# 3. failure categorization
# =====================================================================
def test_traffic_light_failure_is_a_counter_error():
    parsed = parse_simulation_log(FAILING_TRAFFIC_LIGHT_LOG)
    failures = analyze_failures(parsed, FAILING_TRAFFIC_LIGHT_LOG)

    assert len(failures) == 2
    assert all(f.category is FailureCategory.COUNTER_ERROR for f in failures)
    assert failures[0].expected == "A_YELLOW"
    assert failures[0].actual == "B_GREEN"
    assert failures[0].severity is Severity.HIGH


def test_alu_failure_is_an_output_mismatch():
    parsed = parse_simulation_log(FAILING_ALU_LOG)
    failures = analyze_failures(parsed, FAILING_ALU_LOG)

    assert len(failures) == 1
    assert failures[0].category is FailureCategory.OUTPUT_MISMATCH
    assert failures[0].expected == "7"
    assert failures[0].actual == "2"
    # only 1 of 4 tests failed -> MEDIUM, not HIGH
    assert failures[0].severity is Severity.MEDIUM


def test_passing_run_produces_no_failures():
    parsed = parse_simulation_log(PASSING_TRAFFIC_LIGHT_LOG)
    assert analyze_failures(parsed, PASSING_TRAFFIC_LIGHT_LOG) == []


def test_state_mismatch_without_timing_wording_is_an_fsm_error():
    category = categorize_test_failure(
        _test("state check", "A_GREEN", "B_GREEN", "the FSM must be in A_GREEN")
    )
    assert category is FailureCategory.FSM_ERROR


def test_state_mismatch_with_timing_wording_is_a_counter_error():
    category = categorize_test_failure(
        _test("A_YELLOW", "A_YELLOW", "B_GREEN", "must dwell for 4 cycles")
    )
    assert category is FailureCategory.COUNTER_ERROR


def test_numeric_mismatch_is_an_output_mismatch():
    assert categorize_test_failure(_test("OR", "7", "2")) is FailureCategory.OUTPUT_MISMATCH


def test_simulator_assertion_is_an_assertion_failure():
    category = categorize_test_failure(
        _test("assert", "", "", "Assertion failed in traffic_light_tb")
    )
    assert category is FailureCategory.ASSERTION_FAILURE


def test_missing_values_are_unknown():
    assert categorize_test_failure(_test("mystery", "", "")) is FailureCategory.UNKNOWN


def test_compilation_failure_is_critical():
    failure = compilation_failure("syntax error near 'endmodule'")
    assert failure.category is FailureCategory.COMPILATION_ERROR
    assert failure.severity is Severity.CRITICAL


# =====================================================================
# severity rules
# =====================================================================
@pytest.mark.parametrize(
    "category,failed,total,expected",
    [
        (FailureCategory.COMPILATION_ERROR, 1, 4, Severity.CRITICAL),
        (FailureCategory.COUNTER_ERROR, 2, 4, Severity.HIGH),
        (FailureCategory.COUNTER_ERROR, 4, 4, Severity.CRITICAL),
        (FailureCategory.FSM_ERROR, 1, 4, Severity.HIGH),
        (FailureCategory.ASSERTION_FAILURE, 1, 4, Severity.HIGH),
        (FailureCategory.OUTPUT_MISMATCH, 1, 4, Severity.MEDIUM),
        (FailureCategory.OUTPUT_MISMATCH, 3, 4, Severity.HIGH),
        (FailureCategory.UNKNOWN, 1, 4, Severity.MEDIUM),
    ],
)
def test_severity_assignment(category, failed, total, expected):
    assert assign_severity(category, failed, total) is expected


# =====================================================================
# 4. AI response validation
# =====================================================================
def test_valid_ai_response():
    analysis = AIAnalysis(
        rootCause="The OR operation is incorrectly implemented using AND.",
        explanation="For A=6 and B=3 the expected OR result is 7, "
                    "but the RTL performs A & B, producing 2.",
        recommendation="Change the OR operation from A & B to A | B.",
        confidence=0.98,
    )
    assert analysis.confidence == pytest.approx(0.98)
    assert "OR" in analysis.rootCause


def test_percentage_confidence_is_normalised():
    analysis = AIAnalysis(
        rootCause="x", explanation="y", recommendation="z", confidence=95
    )
    assert analysis.confidence == pytest.approx(0.95)


def test_confidence_is_clamped_into_range():
    high = AIAnalysis(rootCause="x", explanation="y", recommendation="z", confidence=250)
    assert high.confidence == 1.0
    low = AIAnalysis(rootCause="x", explanation="y", recommendation="z", confidence=-3)
    assert low.confidence == 0.0


def test_unparsable_confidence_falls_back_to_neutral():
    analysis = AIAnalysis(
        rootCause="x", explanation="y", recommendation="z", confidence="very sure"
    )
    assert analysis.confidence == pytest.approx(0.5)


def test_list_fields_are_flattened_to_text():
    analysis = AIAnalysis(
        rootCause=["bad", "OR"], explanation="y", recommendation="z", confidence=0.5
    )
    assert analysis.rootCause == "bad OR"


def test_empty_root_cause_is_rejected():
    with pytest.raises(ValidationError):
        AIAnalysis(rootCause="", explanation="y", recommendation="z", confidence=0.9)


def test_missing_field_is_rejected():
    with pytest.raises(ValidationError):
        AIAnalysis(rootCause="x", explanation="y", confidence=0.9)


def test_ai_cannot_be_used_to_change_pass_fail():
    """
    Structural guarantee: the AI model has no status/pass/fail field at
    all, so an AI response can never alter the simulator's verdict.
    """
    fields = set(AIAnalysis.model_fields)
    assert fields == {"rootCause", "explanation", "recommendation", "confidence"}
