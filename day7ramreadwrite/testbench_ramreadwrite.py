import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


async def write_word(dut, address, data):
    """Write data to RAM."""

    dut.write_enable.value = 1
    dut.write_address.value = address
    dut.write_data.value = data

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.write_enable.value = 0


async def read_word(dut, address):
    """Read data from RAM."""

    dut.write_enable.value = 0
    dut.read_address.value = address

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    return int(dut.read_data.value)


@cocotb.test()
async def test_ram(dut):

    # Start clock
    cocotb.start_soon(
        Clock(dut.clk, 10, unit="ns").start()
    )

    # Initial values
    dut.write_enable.value = 0
    dut.write_address.value = 0
    dut.read_address.value = 0
    dut.write_data.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    # =====================================
    # TEST 1: Write and read 0xBEEF
    # =====================================

    await write_word(dut, 0x10, 0xBEEF)

    read_value = await read_word(dut, 0x10)

    assert read_value == 0xBEEF, \
        f"Expected 0xBEEF, got 0x{read_value:04X}"

    dut._log.info("TEST 1 PASSED: Write/Read 0xBEEF")

    # =====================================
    # TEST 2: Write and read 0x1234
    # =====================================

    await write_word(dut, 0x20, 0x1234)

    read_value = await read_word(dut, 0x20)

    assert read_value == 0x1234, \
        f"Expected 0x1234, got 0x{read_value:04X}"

    dut._log.info("TEST 2 PASSED: Write/Read 0x1234")

    # =====================================
    # TEST 3: Check previous address
    # =====================================

    read_value = await read_word(dut, 0x10)

    assert read_value == 0xBEEF, \
        f"Expected 0xBEEF, got 0x{read_value:04X}"

    dut._log.info("TEST 3 PASSED: Memory Retention")

    # =====================================
    # TEST 4: Simultaneous write and read
    # =====================================

    dut.write_enable.value = 1
    dut.write_address.value = 0x40
    dut.write_data.value = 0xCAFE

    # Read old address while writing new address
    dut.read_address.value = 0x20

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    read_value = int(dut.read_data.value)

    dut.write_enable.value = 0

    assert read_value == 0x1234, \
        f"Expected 0x1234, got 0x{read_value:04X}"

    dut._log.info("TEST 4 PASSED: Simultaneous Read/Write")

    # =====================================
    # TEST 5: Verify address 0x40
    # =====================================

    read_value = await read_word(dut, 0x40)

    assert read_value == 0xCAFE, \
        f"Expected 0xCAFE, got 0x{read_value:04X}"

    dut._log.info("TEST 5 PASSED: Verify 0xCAFE")

    # =====================================
    # TEST 6: Write 0x0000
    # =====================================

    await write_word(dut, 0x30, 0x0000)

    read_value = await read_word(dut, 0x30)

    assert read_value == 0x0000, \
        f"Expected 0x0000, got 0x{read_value:04X}"

    dut._log.info("TEST 6 PASSED: 0x0000")

    # =====================================
    # TEST 7: Write 0xFFFF
    # =====================================

    await write_word(dut, 0x31, 0xFFFF)

    read_value = await read_word(dut, 0x31)

    assert read_value == 0xFFFF, \
        f"Expected 0xFFFF, got 0x{read_value:04X}"

    dut._log.info("TEST 7 PASSED: 0xFFFF")

    dut._log.info("================================")
    dut._log.info("ALL RAM TESTS PASSED")
    dut._log.info("================================")