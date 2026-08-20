"""Cocotb testbench for 2:1 mux."""
import random
import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_mux2to1_directed(dut):
    """Check all 4 input combinations explicitly."""
    cases = [
        (0, 0, 0, 0),
        (1, 0, 0, 1),
        (0, 1, 0, 0),
        (1, 1, 0, 1),
        (0, 0, 1, 0),
        (1, 0, 1, 0),
        (0, 1, 1, 1),
        (1, 1, 1, 1),
    ]
    for a, b, sel, expected in cases:
        dut.a.value = a
        dut.b.value = b
        dut.sel.value = sel
        await Timer(2, units="ns")
        assert dut.y.value == expected, (
            f"a={a} b={b} sel={sel}: expected y={expected}, got {dut.y.value}"
        )


@cocotb.test()
async def test_mux2to1_random(dut):
    """Randomized check against a Python reference model."""
    for _ in range(50):
        a = random.randint(0, 1)
        b = random.randint(0, 1)
        sel = random.randint(0, 1)
        dut.a.value = a
        dut.b.value = b
        dut.sel.value = sel
        await Timer(2, units="ns")
        expected = b if sel else a
        assert dut.y.value == expected
