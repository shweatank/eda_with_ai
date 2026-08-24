from __future__ import annotations

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def test_up_down_counter(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.reset.value = 1
    dut.up.value = 1
    await Timer(1, unit="ns")
    assert int(dut.count.value) == 0

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    assert int(dut.count.value) == 0

    dut.reset.value = 0
    for expected in range(1, 4):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        assert int(dut.count.value) == expected

    dut.up.value = 0
    for expected in (2, 1, 0, 255):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        assert int(dut.count.value) == expected

    dut.up.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    assert int(dut.count.value) == 0

    dut.reset.value = 1
    await Timer(1, unit="ns")
    assert int(dut.count.value) == 0
