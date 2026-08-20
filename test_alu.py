import random
import cocotb
from cocotb.triggers import Timer

ADD, SUB, MUL, DIV = 0, 1, 2, 3


@cocotb.test()
async def test_add(dut):
    cases = [(0, 0), (255, 255), (100, 50), (1, 1)]
    for a, b in cases:
        dut.a.value = a
        dut.b.value = b
        dut.op.value = ADD
        await Timer(2, units="ns")

        expected = a + b
        actual = int(dut.result.value)
        assert actual == expected, f"ADD a={a} b={b}: got {actual}, expected {expected}"
        dut._log.info(f"PASS ADD: a={a} b={b} -> {actual}")


@cocotb.test()
async def test_sub(dut):
    cases = [(100, 50), (0, 0), (255, 0), (50, 100)]  # last case wraps (unsigned)
    for a, b in cases:
        dut.a.value = a
        dut.b.value = b
        dut.op.value = SUB
        await Timer(2, units="ns")

        expected = (a - b) & 0xFFFF   # unsigned wraparound within 16-bit field
        actual = int(dut.result.value)
        assert actual == expected, f"SUB a={a} b={b}: got {actual}, expected {expected}"
        dut._log.info(f"PASS SUB: a={a} b={b} -> {actual}")


@cocotb.test()
async def test_mul(dut):
    cases = [(0, 0), (255, 255), (16, 16), (1, 200)]
    for a, b in cases:
        dut.a.value = a
        dut.b.value = b
        dut.op.value = MUL
        await Timer(2, units="ns")

        expected = a * b
        actual = int(dut.result.value)
        assert actual == expected, f"MUL a={a} b={b}: got {actual}, expected {expected}"
        dut._log.info(f"PASS MUL: a={a} b={b} -> {actual}")


@cocotb.test()
async def test_div(dut):
    cases = [(10, 2), (255, 1), (7, 3), (0, 5)]
    for a, b in cases:
        dut.a.value = a
        dut.b.value = b
        dut.op.value = DIV
        await Timer(2, units="ns")

        expected_q = a // b
        expected_r = a % b
        actual_q = int(dut.result.value)
        actual_r = int(dut.remainder.value)

        assert actual_q == expected_q, f"DIV a={a} b={b}: quotient got {actual_q}, expected {expected_q}"
        assert actual_r == expected_r, f"DIV a={a} b={b}: remainder got {actual_r}, expected {expected_r}"
        assert dut.div_by_zero.value == 0
        dut._log.info(f"PASS DIV: a={a} b={b} -> q={actual_q} r={actual_r}")


@cocotb.test()
async def test_div_by_zero(dut):
    dut.a.value = 42
    dut.b.value = 0
    dut.op.value = DIV
    await Timer(2, units="ns")

    assert dut.div_by_zero.value == 1, "div_by_zero should assert when b=0"
    dut._log.info("PASS: div_by_zero correctly flagged")


@cocotb.test()
async def test_random_all_ops(dut):
    """Randomized regression across all four operations."""
    errors = 0
    num_tests = 500

    for _ in range(num_tests):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        op = random.choice([ADD, SUB, MUL, DIV])

        dut.a.value = a
        dut.b.value = b
        dut.op.value = op
        await Timer(2, units="ns")

        if op == ADD:
            expected = a + b
            actual = int(dut.result.value)
        elif op == SUB:
            expected = (a - b) & 0xFFFF
            actual = int(dut.result.value)
        elif op == MUL:
            expected = a * b
            actual = int(dut.result.value)
        elif op == DIV:
            if b == 0:
                if dut.div_by_zero.value != 1:
                    dut._log.error(f"DIV a={a} b=0: div_by_zero not set")
                    errors += 1
                continue
            expected = a // b
            actual = int(dut.result.value)

        if actual != expected:
            dut._log.error(f"FAIL op={op} a={a} b={b}: got {actual}, expected {expected}")
            errors += 1

    assert errors == 0, f"{errors}/{num_tests} mismatch(es) found"