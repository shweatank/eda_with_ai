"""Cocotb testbench for 4-bit up/down counter."""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def test_counter_reset_and_count_up(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.rst.value = 1
    dut.en.value = 0
    dut.up_down.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    assert dut.count.value == 0

    dut.rst.value = 0
    dut.en.value = 1
    expected = 0
    for _ in range(20):
        await RisingEdge(dut.clk)
        await Timer(1, units="ns")
        expected = (expected + 1) & 0xF
        assert dut.count.value == expected, f"expected {expected}, got {dut.count.value}"


@cocotb.test()
async def test_counter_down_and_enable(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.rst.value = 1
    dut.en.value = 0
    dut.up_down.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    dut.rst.value = 0

    # enable off: count should not change
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    assert dut.count.value == 0

    dut.en.value = 1
    expected = 0
    for _ in range(20):
        await RisingEdge(dut.clk)
        await Timer(1, units="ns")
        expected = (expected - 1) & 0xF
        assert dut.count.value == expected, f"expected {expected}, got {dut.count.value}"
