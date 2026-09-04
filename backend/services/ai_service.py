"""
Groq AI service -- explains a failure the simulator has ALREADY found.

Hard boundaries:
  * Groq is called only when there is at least one failed test.
  * Groq receives evidence only: RTL source, testbench name, the real
    simulation log, the failed test, expected/actual, and the category
    that `failure_analyzer` decided deterministically.
  * Groq never decides PASS/FAIL and is explicitly told not to invent
    test results.
  * The response is validated with Pydantic; an unusable response falls
    back to a clearly-labelled deterministic summary rather than crashing
    the verification run.
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Optional

from backend.config import settings
from backend.models.schemas import AIAnalysis, FailureInfo, ParsedLog

log = logging.getLogger(__name__)

MAX_RTL_CHARS = 4000
MAX_LOG_CHARS = 4000

SYSTEM_PROMPT = """\
You are an expert RTL verification engineer performing root-cause analysis \
on a SystemVerilog design.

Rules you MUST follow:
1. The simulator has already decided which tests pass and which fail. Never \
contradict it, never re-judge a test, and never invent test results, values \
or tests that are not in the evidence.
2. Base your analysis ONLY on the evidence provided in the user message.
3. Point at the specific line/expression in the RTL that causes the failure.
4. If the evidence is insufficient, say so plainly and lower your confidence.

Respond with a single JSON object and nothing else, using exactly these keys:
{
  "rootCause":      "one sentence naming the defect in the RTL",
  "explanation":    "2-4 sentences citing the expected vs actual evidence",
  "recommendation": "the concrete code change that fixes it",
  "confidence":     0.0 to 1.0
}"""


class AIServiceError(RuntimeError):
    pass


def _read_source(path: Optional[str], limit: int = MAX_RTL_CHARS) -> str:
    if not path:
        return "(source unavailable)"
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return f"(could not read {path}: {exc})"
    if len(text) > limit:
        return text[:limit] + f"\n... (truncated at {limit} chars)"
    return text


def _tail(text: str, limit: int = MAX_LOG_CHARS) -> str:
    text = text or ""
    return text if len(text) <= limit else "... (truncated)\n" + text[-limit:]


def build_evidence_prompt(
    example: str,
    scenario: str,
    rtl_path: Optional[str],
    testbench_path: Optional[str],
    parsed: ParsedLog,
    failure: FailureInfo,
    simulation_log: str,
) -> str:
    """Assemble the evidence block. Nothing here is speculative."""
    failing_lines = "\n".join(
        f"  - {t.test_id} ({t.name}): expected={t.expected!r} actual={t.actual!r}"
        for t in parsed.failed
    ) or "  (none)"
    passing_lines = "\n".join(
        f"  - {t.test_id} ({t.name}): PASS" for t in parsed.passed
    ) or "  (none)"

    return f"""\
=== DESIGN UNDER VERIFICATION ===
Example : {example}
Scenario: {scenario}

=== RTL SOURCE ({Path(rtl_path).name if rtl_path else 'unknown'}) ===
{_read_source(rtl_path)}

=== TESTBENCH ===
File: {Path(testbench_path).name if testbench_path else 'unknown'}
The testbench is known-good and is IDENTICAL for the passing and failing
scenarios. Therefore the defect is in the RTL, not in the testbench.

=== SIMULATOR VERDICT (authoritative -- do not change it) ===
Total tests : {parsed.total_tests}
Passed      : {parsed.passed_tests}
Failed      : {parsed.failed_tests}
Overall     : {parsed.status.value}

Passing tests:
{passing_lines}

Failing tests:
{failing_lines}

=== FAILURE UNDER ANALYSIS ===
Test           : {failure.test_id} ({failure.test_name})
Category       : {failure.category.value}   (decided by static rules, not by you)
Severity       : {failure.severity.value}
Expected value : {failure.expected}
Actual value   : {failure.actual}
Check intent   : {failure.message}

=== RAW SIMULATION LOG (vvp stdout) ===
{_tail(simulation_log)}

Explain the root cause of the failing test above and how to fix the RTL.
Return only the JSON object."""


def _extract_json(text: str) -> dict:
    """Pull a JSON object out of a model response, tolerating stray prose."""
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # first {...} balanced-ish block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise ValueError("no JSON object found in model response")


def _fallback(failure: FailureInfo, reason: str) -> AIAnalysis:
    """Deterministic, honestly-labelled stand-in when Groq is unusable."""
    return AIAnalysis(
        rootCause=(
            f"[AI unavailable] Deterministic classification: "
            f"{failure.category.value} in {failure.test_name or failure.test_id}."
        ),
        explanation=(
            f"The simulator reported {failure.test_id} as FAIL: expected "
            f"{failure.expected!r} but the design produced {failure.actual!r}. "
            f"AI narration was not available ({reason})."
        ),
        recommendation=(
            "Inspect the RTL expression that drives this output and compare it "
            "against the testbench's stated intent: "
            f"{failure.message or 'see simulation.log'}"
        ),
        confidence=0.3,
    )


class AIService:
    def __init__(self) -> None:
        self._client = None

    def _get_client(self):
        if self._client is None:
            if not settings.groq_configured:
                raise AIServiceError(
                    "GROQ_API_KEY is not set. Add it to .env to enable AI analysis."
                )
            try:
                from groq import Groq
            except ImportError as exc:                       # pragma: no cover
                raise AIServiceError(
                    "The `groq` package is not installed (pip install -r requirements.txt)"
                ) from exc
            self._client = Groq(api_key=settings.GROQ_API_KEY)
        return self._client

    def analyze_failure(
        self,
        example: str,
        scenario: str,
        rtl_path: Optional[str],
        testbench_path: Optional[str],
        parsed: ParsedLog,
        failure: FailureInfo,
        simulation_log: str,
    ) -> AIAnalysis:
        """
        Ask Groq to explain one failure. Always returns a valid AIAnalysis:
        on any error the deterministic fallback is used so the verification
        job still completes and still gets stored in Neo4j.
        """
        prompt = build_evidence_prompt(
            example, scenario, rtl_path, testbench_path,
            parsed, failure, simulation_log,
        )

        try:
            client = self._get_client()
        except AIServiceError as exc:
            log.warning("Groq unavailable: %s", exc)
            return _fallback(failure, str(exc))

        try:
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=900,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content
        except Exception as exc:
            msg = self._scrub(f"{type(exc).__name__}: {exc}")
            log.error("Groq API call failed: %s", msg)
            return _fallback(failure, f"Groq API error: {msg[:200]}")

        try:
            payload = _extract_json(raw)
            # tolerate snake_case keys from a chatty model
            normalised = {
                "rootCause": payload.get("rootCause") or payload.get("root_cause"),
                "explanation": payload.get("explanation"),
                "recommendation": (
                    payload.get("recommendation") or payload.get("fix")
                ),
                "confidence": payload.get("confidence"),
            }
            return AIAnalysis(**normalised)
        except Exception as exc:
            log.error("Invalid AI response (%s): %r", type(exc).__name__, raw[:300])
            return _fallback(failure, f"invalid AI response: {type(exc).__name__}")

    @staticmethod
    def _scrub(text: str) -> str:
        out = text
        for secret in (settings.GROQ_API_KEY, settings.NEO4J_PASSWORD):
            if secret:
                out = out.replace(secret, "***")
        return out


ai_service = AIService()
