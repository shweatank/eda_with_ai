"""Cocotb testbench for D flip-flop."""
import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def test_dff_reset(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.rst_n.value = 0
    dut.d.value = 1
    await Timer(15, units="ns")
    assert dut.q.value == 0, "q should be 0 during reset"
    dut.rst_n.value = 1


@cocotb.test()
async def test_dff_capture(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.rst_n.value = 1
    dut.d.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    for _ in range(30):
        d_val = random.randint(0, 1)
        dut.d.value = d_val
        await RisingEdge(dut.clk)
        await Timer(1, units="ns")  # allow non-blocking assignment to settle
        assert dut.q.value == d_val, f"expected q={d_val}, got {dut.q.value}"
