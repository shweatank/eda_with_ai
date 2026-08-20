"""Cocotb testbench for 4:1 mux."""
import random
import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_mux4to1_directed(dut):
    d = 0b1010  # d3=1 d2=0 d1=1 d0=0
    dut.d.value = d
    for sel in range(4):
        dut.sel.value = sel
        await Timer(2, units="ns")
        expected = (d >> sel) & 1
        assert dut.y.value == expected, f"sel={sel}: expected {expected}, got {dut.y.value}"


@cocotb.test()
async def test_mux4to1_random(dut):
    for _ in range(50):
        d = random.randint(0, 15)
        sel = random.randint(0, 3)
        dut.d.value = d
        dut.sel.value = sel
        await Timer(2, units="ns")
        expected = (d >> sel) & 1
        assert dut.y.value == expected
