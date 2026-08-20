"""Cocotb testbench for 4-bit magnitude comparator."""
import random
import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_comparator4_edge_cases(dut):
    cases = [(0, 0), (15, 15), (0, 15), (15, 0), (5, 5), (7, 8)]
    for a, b in cases:
        dut.a.value = a
        dut.b.value = b
        await Timer(2, units="ns")
        assert dut.a_gt_b.value == (a > b)
        assert dut.a_eq_b.value == (a == b)
        assert dut.a_lt_b.value == (a < b)


@cocotb.test()
async def test_comparator4_random(dut):
    for _ in range(80):
        a = random.randint(0, 15)
        b = random.randint(0, 15)
        dut.a.value = a
        dut.b.value = b
        await Timer(2, units="ns")
        assert dut.a_gt_b.value == (a > b)
        assert dut.a_eq_b.value == (a == b)
        assert dut.a_lt_b.value == (a < b)
