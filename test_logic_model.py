import itertools
import cocotb
from cocotb.triggers import Timer
from cocotb.regression import TestFactory


@cocotb.test()
async def test_exhaustive(dut):
    """Exhaustively test all 8 input combinations against the expected logic."""

    errors = 0

    for a, b, c in itertools.product([0, 1], repeat=3):
        dut.a.value = a
        dut.b.value = b
        dut.c.value = c

        await Timer(10, units="ns")  # allow combinational logic to settle

        expected = (a & b) | c
        actual = dut.y.value

        if actual != expected:
            dut._log.error(
                f"FAIL: a={a} b={b} c={c} -> y={actual} (expected {expected})"
            )
            errors += 1
        else:
            dut._log.info(f"PASS: a={a} b={b} c={c} -> y={actual}")

    assert errors == 0, f"{errors} mismatch(es) found in exhaustive test"


@cocotb.test()
async def test_random(dut):
    """Randomized regression test as a supplement to exhaustive coverage."""
    import random

    for _ in range(50):
        a = random.randint(0, 1)
        b = random.randint(0, 1)
        c = random.randint(0, 1)

        dut.a.value = a
        dut.b.value = b
        dut.c.value = c

        await Timer(10, units="ns")

        expected = (a & b) | c
        assert dut.y.value == expected, (
            f"Mismatch: a={a} b={b} c={c} -> y={dut.y.value} "
            f"(expected {expected})"
        )