"""Cocotb testbench for simple_ram (16-bit data width).

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
    """Write/read regression test for the 16-bit-wide simple_ram."""

    # Start a 10 ns period clock
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Reset-like initial drive values
    dut.write_enable.value = 0
    dut.address.value = 0
    dut.write_data.value = 0
    await RisingEdge(dut.clk)

    # ---------------------------------------------------------
    # Test 1: Write 0xBEEF to address 0x10
    # ---------------------------------------------------------
    await write_word(dut, 0x10, 0xBEEF)
    dut._log.info("Wrote 0xBEEF to address 0x10")

    # ---------------------------------------------------------
    # Test 2: Read address 0x10
    # ---------------------------------------------------------
    read_value = await read_word(dut, 0x10)
    dut._log.info(f"Read address 0x10 = 0x{read_value:04X}")
    assert read_value == 0xBEEF, f"Expected 0xBEEF, got 0x{read_value:04X}"

    # ---------------------------------------------------------
    # Test 3: Write 0x1234 to address 0x20
    # ---------------------------------------------------------
    await write_word(dut, 0x20, 0x1234)
    dut._log.info("Wrote 0x1234 to address 0x20")

    # ---------------------------------------------------------
    # Test 4: Read address 0x20
    # ---------------------------------------------------------
    read_value = await read_word(dut, 0x20)
    dut._log.info(f"Read address 0x20 = 0x{read_value:04X}")
    assert read_value == 0x1234, f"Expected 0x1234, got 0x{read_value:04X}"

    # ---------------------------------------------------------
    # Test 5: Verify address 0x10 still contains 0xBEEF
    # ---------------------------------------------------------
    read_value = await read_word(dut, 0x10)
    dut._log.info(f"Read address 0x10 again = 0x{read_value:04X}")
    assert read_value == 0xBEEF, f"Expected 0xBEEF, got 0x{read_value:04X}"

    # ---------------------------------------------------------
    # Test 6: Full-width boundary values (all zeros / all ones)
    # ---------------------------------------------------------
    await write_word(dut, 0x30, 0x0000)
    read_value = await read_word(dut, 0x30)
    assert read_value == 0x0000, f"Expected 0x0000, got 0x{read_value:04X}"

    await write_word(dut, 0x31, 0xFFFF)
    read_value = await read_word(dut, 0x31)
    assert read_value == 0xFFFF, f"Expected 0xFFFF, got 0x{read_value:04X}"
    dut._log.info("Boundary values 0x0000 / 0xFFFF verified at 0x30 / 0x31")

    dut._log.info("=" * 37)
    dut._log.info("   SIMPLE RAM (16-BIT) TEST PASSED  ")
    dut._log.info("=" * 37)