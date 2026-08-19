import os
import cocotb
from cocotb.triggers import Timer

from gate_analysis import summarize_gate_results, explain_truth_table

# Set ENABLE_LLM_ANALYSIS=1 in your environment to turn the Gemini
# analysis calls back on. Off by default -- keeps tests fast, avoids
# rate limits, and avoids LLM failures ever affecting test results.
ENABLE_LLM_ANALYSIS = os.environ.get("ENABLE_LLM_ANALYSIS", "0") == "1"

# Collects results per-gate so we can build a truth table and summary
# after each gate's test finishes.
_results_by_gate = {}


async def check(dut, a, b, expected, gate_name, has_b=True):
    dut.a.value = a
    if has_b:
        dut.b.value = b
    await Timer(1, unit="ns")
    actual = int(dut.y.value)

    inputs = (a, b) if has_b else (a,)
    result = {
        "gate": gate_name,
        "inputs": inputs,
        "output": actual,
        "expected": expected,
        "pass": actual == expected,
    }
    _results_by_gate.setdefault(gate_name, []).append(result)

    if has_b:
        assert actual == expected, f"{gate_name}: {a} , {b} -> expected {expected}, got {actual}"
        print(f"PASS: {a} {gate_name} {b} = {actual}")
    else:
        assert actual == expected, f"{gate_name}: {a} -> expected {expected}, got {actual}"
        print(f"PASS: {gate_name} {a} = {actual}")


def _analyze_gate(gate_name):
    """Build a truth table + summary for one gate and print Gemini's analysis.

    Skipped entirely unless ENABLE_LLM_ANALYSIS=1 is set. Wrapped in
    try/except regardless: an LLM failure (rate limit, network issue,
    etc.) should never cause the actual hardware test to fail.
    """
    if not ENABLE_LLM_ANALYSIS:
        return

    results = _results_by_gate.get(gate_name, [])
    if not results:
        return

    truth_table = {tuple(r["inputs"]): r["output"] for r in results}

    print(f"\n--- Gemini analysis: {gate_name} ---")
    try:
        print(explain_truth_table(gate_name, truth_table))
        print(summarize_gate_results(results))
    except Exception as e:
        print(f"[Gemini analysis skipped: {e}]")
    print("---------------------------------\n")


@cocotb.test()
async def test_and(dut):
    await check(dut, 0, 0, 0, "AND")
    await check(dut, 0, 1, 0, "AND")
    await check(dut, 1, 0, 0, "AND")
    await check(dut, 1, 1, 1, "AND")
    _analyze_gate("AND")


@cocotb.test()
async def test_or(dut):
    await check(dut, 0, 0, 0, "OR")
    await check(dut, 0, 1, 1, "OR")
    await check(dut, 1, 0, 1, "OR")
    await check(dut, 1, 1, 1, "OR")
    _analyze_gate("OR")


@cocotb.test()
async def test_not(dut):
    await check(dut, 0, None, 1, "NOT", has_b=False)
    await check(dut, 1, None, 0, "NOT", has_b=False)
    _analyze_gate("NOT")


@cocotb.test()
async def test_xor(dut):
    await check(dut, 0, 0, 0, "XOR")
    await check(dut, 0, 1, 1, "XOR")
    await check(dut, 1, 0, 1, "XOR")
    await check(dut, 1, 1, 0, "XOR")
    _analyze_gate("XOR")


@cocotb.test()
async def test_nand(dut):
    await check(dut, 0, 0, 1, "NAND")
    await check(dut, 0, 1, 1, "NAND")
    await check(dut, 1, 0, 1, "NAND")
    await check(dut, 1, 1, 0, "NAND")
    _analyze_gate("NAND")


@cocotb.test()
async def test_nor(dut):
    await check(dut, 0, 0, 1, "NOR")
    await check(dut, 0, 1, 0, "NOR")
    await check(dut, 1, 0, 0, "NOR")
    await check(dut, 1, 1, 0, "NOR")
    _analyze_gate("NOR")


@cocotb.test()
async def test_xnor(dut):
    await check(dut, 0, 0, 1, "XNOR")
    await check(dut, 0, 1, 0, "XNOR")
    await check(dut, 1, 0, 0, "XNOR")
    await check(dut, 1, 1, 1, "XNOR")
    _analyze_gate("XNOR")