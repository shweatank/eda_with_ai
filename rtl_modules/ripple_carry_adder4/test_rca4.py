"""Cocotb testbench for 4-bit ripple carry adder."""
import random
import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_rca4_directed(dut):
    cases = [(0, 0, 0), (5, 3, 0), (15, 1, 0), (15, 15, 1), (7, 8, 1)]
    for a, b, cin in cases:
        dut.a.value = a
        dut.b.value = b
        dut.cin.value = cin
        await Timer(2, units="ns")
        expected = a + b + cin
        got = int(dut.sum.value) | (int(dut.cout.value) << 4)
        assert got == expected, f"a={a} b={b} cin={cin}: expected {expected}, got {got}"


@cocotb.test()
async def test_rca4_random(dut):
    for _ in range(100):
        a = random.randint(0, 15)
        b = random.randint(0, 15)
        cin = random.randint(0, 1)
        dut.a.value = a
        dut.b.value = b
        dut.cin.value = cin
        await Timer(2, units="ns")
        expected = a + b + cin
        got = int(dut.sum.value) | (int(dut.cout.value) << 4)
        assert got == expected
