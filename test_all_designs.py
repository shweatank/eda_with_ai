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


"""
test_designs.py

One cocotb test file covering every module in designs.v. Each run only
elaborates ONE module as TOPLEVEL and only executes ONE test function via
COCOTB_TESTCASE -- so a test function only ever sees the `dut` its ports
were written for. Never run this file's tests in bulk against a single
TOPLEVEL; the GUI (main.py) always pairs a testcase with its matching
toplevel from the MODULES list.
"""
import random
import itertools

import cocotb
from cocotb.triggers import Timer


# ---------------------------------------------------------------- logic_model
@cocotb.test()
async def test_logic_exhaustive(dut):
    errors = 0
    for a, b, c in itertools.product([0, 1], repeat=3):
        dut.a.value = a
        dut.b.value = b
        dut.c.value = c
        await Timer(2, unit="ns")
        expected = (a & b) | c
        actual = dut.y.value
        if actual != expected:
            dut._log.error(f"FAIL: a={a} b={b} c={c} -> y={actual} (expected {expected})")
            errors += 1
        else:
            print(f"PASS: a={a} b={b} c={c} -> y={actual}")
    assert errors == 0, f"{errors} mismatch(es) found"


# ------------------------------------------------------------------- adder
@cocotb.test()
async def test_add_edge(dut):
    cases = [(0, 0), (255, 255), (255, 0), (0, 255), (1, 1), (128, 127), (200, 100)]
    for a, b in cases:
        dut.a.value = a
        dut.b.value = b
        await Timer(2, unit="ns")
        expected = a + b
        actual = int(dut.y.value)
        assert actual == expected, f"a={a} b={b}: got {actual}, expected {expected}"
        print(f"PASS: a={a} b={b} -> y={actual}")


@cocotb.test()
async def test_add_random(dut):
    errors = 0
    for _ in range(200):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        dut.a.value = a
        dut.b.value = b
        await Timer(2, unit="ns")
        expected = a + b
        actual = int(dut.y.value)
        if actual != expected:
            dut._log.error(f"FAIL: a={a} b={b} -> y={actual} (expected {expected})")
            errors += 1
    assert errors == 0, f"{errors}/200 mismatch(es) found"
    print("PASS: random regression clean")


# --------------------------------------------------------------- subtractor
def _to_signed(val, bits):
    if val >= (1 << (bits - 1)):
        val -= (1 << bits)
    return val


@cocotb.test()
async def test_sub_edge(dut):
    cases = [(100, 50), (0, 0), (255, 0), (50, 100)]  # last case wraps (unsigned)
    for a, b in cases:
        dut.a.value = a
        dut.b.value = b
        await Timer(2, unit="ns")
        expected = _to_signed((a - b) & 0x1FF, 9)
        actual = _to_signed(int(dut.y.value), 9)
        assert actual == expected, f"a={a} b={b}: got {actual}, expected {expected}"
        print(f"PASS: a={a} b={b} -> y={actual}")


@cocotb.test()
async def test_sub_random(dut):
    errors = 0
    for _ in range(200):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        dut.a.value = a
        dut.b.value = b
        await Timer(2, unit="ns")
        expected = _to_signed((a - b) & 0x1FF, 9)
        actual = _to_signed(int(dut.y.value), 9)
        if actual != expected:
            dut._log.error(f"FAIL: a={a} b={b} -> y={actual} (expected {expected})")
            errors += 1
    assert errors == 0, f"{errors}/200 mismatch(es) found"
    print("PASS: random regression clean")


# --------------------------------------------------------------- multiplier
@cocotb.test()
async def test_mul_edge(dut):
    cases = [(0, 0), (0, 255), (255, 0), (1, 1), (255, 255), (128, 2), (16, 16)]
    for a, b in cases:
        dut.a.value = a
        dut.b.value = b
        await Timer(2, unit="ns")
        expected = a * b
        actual = int(dut.y.value)
        assert actual == expected, f"a={a} b={b}: got {actual}, expected {expected}"
        print(f"PASS: a={a} b={b} -> y={actual}")


@cocotb.test()
async def test_mul_random(dut):
    errors = 0
    for _ in range(200):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        dut.a.value = a
        dut.b.value = b
        await Timer(2, unit="ns")
        expected = a * b
        actual = int(dut.y.value)
        if actual != expected:
            dut._log.error(f"FAIL: a={a} b={b} -> y={actual} (expected {expected})")
            errors += 1
    assert errors == 0, f"{errors}/200 mismatch(es) found"
    print("PASS: random regression clean")


# ------------------------------------------------------------------ divider
@cocotb.test()
async def test_div_edge(dut):
    cases = [(10, 2), (255, 1), (7, 3), (0, 5), (255, 255), (100, 7)]
    for a, b in cases:
        dut.a.value = a
        dut.b.value = b
        await Timer(2, unit="ns")
        expected_q = a // b
        expected_r = a % b
        actual_q = int(dut.quotient.value)
        actual_r = int(dut.remainder.value)
        assert actual_q == expected_q, f"a={a} b={b}: quotient got {actual_q}, expected {expected_q}"
        assert actual_r == expected_r, f"a={a} b={b}: remainder got {actual_r}, expected {expected_r}"
        assert dut.div_by_zero.value == 0
        print(f"PASS: a={a} b={b} -> q={actual_q} r={actual_r}")


@cocotb.test()
async def test_div_by_zero(dut):
    dut.a.value = 42
    dut.b.value = 0
    await Timer(2, unit="ns")
    assert dut.div_by_zero.value == 1, "div_by_zero should assert when b=0"
    print("PASS: div_by_zero correctly flagged for b=0")


@cocotb.test()
async def test_div_random(dut):
    errors = 0
    for _ in range(200):
        a = random.randint(0, 255)
        b = random.randint(1, 255)  # avoid zero here; covered by test_div_by_zero
        dut.a.value = a
        dut.b.value = b
        await Timer(2, unit="ns")
        expected_q = a // b
        expected_r = a % b
        actual_q = int(dut.quotient.value)
        actual_r = int(dut.remainder.value)
        if actual_q != expected_q or actual_r != expected_r:
            dut._log.error(
                f"FAIL: a={a} b={b} -> q={actual_q} (exp {expected_q}), r={actual_r} (exp {expected_r})"
            )
            errors += 1
    assert errors == 0, f"{errors}/200 mismatch(es) found"
    print("PASS: random regression clean")


# ---------------------------------------------------------------------- alu
ADD, SUB, MUL, DIV = 0, 1, 2, 3


@cocotb.test()
async def test_alu_add(dut):
    cases = [(0, 0), (255, 255), (100, 50), (1, 1)]
    for a, b in cases:
        dut.a.value = a
        dut.b.value = b
        dut.op.value = ADD
        await Timer(2, unit="ns")
        expected = a + b
        actual = int(dut.result.value)
        assert actual == expected, f"ADD a={a} b={b}: got {actual}, expected {expected}"
        print(f"PASS ADD: a={a} b={b} -> {actual}")


@cocotb.test()
async def test_alu_sub(dut):
    cases = [(100, 50), (0, 0), (255, 0), (50, 100)]
    for a, b in cases:
        dut.a.value = a
        dut.b.value = b
        dut.op.value = SUB
        await Timer(2, unit="ns")
        expected = (a - b) & 0xFFFF
        actual = int(dut.result.value)
        assert actual == expected, f"SUB a={a} b={b}: got {actual}, expected {expected}"
        print(f"PASS SUB: a={a} b={b} -> {actual}")


@cocotb.test()
async def test_alu_mul(dut):
    cases = [(0, 0), (255, 255), (16, 16), (1, 200)]
    for a, b in cases:
        dut.a.value = a
        dut.b.value = b
        dut.op.value = MUL
        await Timer(2, unit="ns")
        expected = a * b
        actual = int(dut.result.value)
        assert actual == expected, f"MUL a={a} b={b}: got {actual}, expected {expected}"
        print(f"PASS MUL: a={a} b={b} -> {actual}")


@cocotb.test()
async def test_alu_div(dut):
    cases = [(10, 2), (255, 1), (7, 3), (0, 5)]
    for a, b in cases:
        dut.a.value = a
        dut.b.value = b
        dut.op.value = DIV
        await Timer(2, unit="ns")
        expected_q = a // b
        expected_r = a % b
        actual_q = int(dut.result.value)
        actual_r = int(dut.remainder.value)
        assert actual_q == expected_q, f"DIV a={a} b={b}: quotient got {actual_q}, expected {expected_q}"
        assert actual_r == expected_r, f"DIV a={a} b={b}: remainder got {actual_r}, expected {expected_r}"
        assert dut.div_by_zero.value == 0
        print(f"PASS DIV: a={a} b={b} -> q={actual_q} r={actual_r}")


@cocotb.test()
async def test_alu_div_by_zero(dut):
    dut.a.value = 42
    dut.b.value = 0
    dut.op.value = DIV
    await Timer(2, unit="ns")
    assert dut.div_by_zero.value == 1, "div_by_zero should assert when b=0"
    print("PASS: div_by_zero correctly flagged")


@cocotb.test()
async def test_alu_random(dut):
    errors = 0
    num_tests = 300
    for _ in range(num_tests):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        op = random.choice([ADD, SUB, MUL, DIV])
        dut.a.value = a
        dut.b.value = b
        dut.op.value = op
        await Timer(2, unit="ns")

        if op == ADD:
            expected, actual = a + b, int(dut.result.value)
        elif op == SUB:
            expected, actual = (a - b) & 0xFFFF, int(dut.result.value)
        elif op == MUL:
            expected, actual = a * b, int(dut.result.value)
        else:  # DIV
            if b == 0:
                if dut.div_by_zero.value != 1:
                    dut._log.error(f"DIV a={a} b=0: div_by_zero not set")
                    errors += 1
                continue
            expected, actual = a // b, int(dut.result.value)

        if actual != expected:
            dut._log.error(f"FAIL op={op} a={a} b={b}: got {actual}, expected {expected}")
            errors += 1

    assert errors == 0, f"{errors}/{num_tests} mismatch(es) found"
    print("PASS: random regression clean across all ops")

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def test_dff_1bit(dut):
    """Verify reset, storage and data capture."""

    # Start a 10 ns clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Set initial inputs
    dut.reset.value = 1
    dut.d.value = 0

    await Timer(2, units="ns")

    # Asynchronous reset must clear q immediately
    assert dut.q.value == 0, (
        f"Reset failed: expected q=0, received q={dut.q.value}"
    )

    cocotb.log.info("PASS: Reset cleared q")

    # Release reset
    dut.reset.value = 0

    # Test storing 1
    dut.d.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert dut.q.value == 1, (
        f"Store-1 failed: expected q=1, received q={dut.q.value}"
    )

    cocotb.log.info("PASS: DFF stored 1")

    # Change d between clock edges
    dut.d.value = 0
    await Timer(2, units="ns")

    # q must retain its previous value until the next edge
    assert dut.q.value == 1, (
        f"Storage failed: q changed before clock edge to {dut.q.value}"
    )

    cocotb.log.info("PASS: DFF retained previous value")

    # Capture 0 on the next rising edge
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert dut.q.value == 0, (
        f"Store-0 failed: expected q=0, received q={dut.q.value}"
    )

    cocotb.log.info("PASS: DFF stored 0")

    # Test asynchronous reset while q contains 1
    dut.d.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert dut.q.value == 1

    # Assert reset without waiting for a clock edge
    dut.reset.value = 1
    await Timer(1, units="ns")

    assert dut.q.value == 0, (
        f"Asynchronous reset failed: q={dut.q.value}"
    )

    cocotb.log.info("PASS: Asynchronous reset worked")
    cocotb.log.info("ALL D FLIP-FLOP TESTS PASSED")