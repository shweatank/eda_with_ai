"""Cocotb testbench for simple_ram.

Verifies basic write/read behaviour and that previously written
locations retain their values after other addresses are written.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


async def write_word(dut, address, data):
    """Drive a single synchronous write into the RAM."""
    dut.write_enable.value = 1
    dut.address.value = address
    dut.write_data.value = data
    await RisingEdge(dut.clk)


async def read_word(dut, address):
    """Drive a synchronous read and return the resulting read_data."""
    dut.write_enable.value = 0
    dut.address.value = address
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return int(dut.read_data.value)


@cocotb.test()
async def test_simple_ram(dut):
    """Write/read regression test for simple_ram."""

    # Start a 10 ns period clock
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Reset-like initial drive values
    dut.write_enable.value = 0
    dut.address.value = 0
    dut.write_data.value = 0
    await RisingEdge(dut.clk)

    # ---------------------------------------------------------
    # Test 1: Write 0xAA to address 0x10
    # ---------------------------------------------------------
    await write_word(dut, 0x10, 0xAA)
    dut._log.info("Wrote 0xAA to address 0x10")

    # ---------------------------------------------------------
    # Test 2: Read address 0x10
    # ---------------------------------------------------------
    read_value = await read_word(dut, 0x10)
    dut._log.info(f"Read address 0x10 = 0x{read_value:02X}")
    assert read_value == 0xAA, f"Expected 0xAA, got 0x{read_value:02X}"

    # ---------------------------------------------------------
    # Test 3: Write 0x55 to address 0x20
    # ---------------------------------------------------------
    await write_word(dut, 0x20, 0x55)
    dut._log.info("Wrote 0x55 to address 0x20")

    # ---------------------------------------------------------
    # Test 4: Read address 0x20
    # ---------------------------------------------------------
    read_value = await read_word(dut, 0x20)
    dut._log.info(f"Read address 0x20 = 0x{read_value:02X}")
    assert read_value == 0x55, f"Expected 0x55, got 0x{read_value:02X}"

    # ---------------------------------------------------------
    # Test 5: Verify address 0x10 still contains 0xAA
    # ---------------------------------------------------------
    read_value = await read_word(dut, 0x10)
    dut._log.info(f"Read address 0x10 again = 0x{read_value:02X}")
    assert read_value == 0xAA, f"Expected 0xAA, got 0x{read_value:02X}"

    dut._log.info("=" * 37)
    dut._log.info("      SIMPLE RAM TEST PASSED       ")
    dut._log.info("=" * 37)