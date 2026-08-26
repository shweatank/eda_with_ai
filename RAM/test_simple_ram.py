import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def test_simple_ram(dut):
    # Start 10 ns clock
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Initial values
    dut.write_enable.value = 0
    dut.address.value = 0
    dut.write_data.value = 0
    await RisingEdge(dut.clk)

    # -------------------------------------------------
    # Test 1: Write 0xAA to address 0x10
    # -------------------------------------------------
    dut.write_enable.value = 1
    dut.address.value = 0x10
    dut.write_data.value = 0xAA
    await RisingEdge(dut.clk)
    print("Wrote 0xAA to address 0x10")

    # -------------------------------------------------
    # Test 2: Read address 0x10
    # -------------------------------------------------
    dut.write_enable.value = 0
    dut.address.value = 0x10
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    read_value = int(dut.read_data.value)
    print(f"Read address 0x10 = 0x{read_value:02X}")
    assert read_value == 0xAA, \
        f"Expected 0xAA, got 0x{read_value:02X}"

    # -------------------------------------------------
    # Test 3: Write 0x55 to address 0x20
    # -------------------------------------------------
    dut.write_enable.value = 1
    dut.address.value = 0x20
    dut.write_data.value = 0x55
    await RisingEdge(dut.clk)
    print("Wrote 0x55 to address 0x20")

    # -------------------------------------------------
    # Test 4: Read address 0x20
    # -------------------------------------------------
    dut.write_enable.value = 0
    dut.address.value = 0x20
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    read_value = int(dut.read_data.value)
    print(f"Read address 0x20 = 0x{read_value:02X}")
    assert read_value == 0x55, \
        f"Expected 0x55, got 0x{read_value:02X}"

    # -------------------------------------------------
    # Test 5: Verify address 0x10 still contains 0xAA
    # -------------------------------------------------
    dut.address.value = 0x10
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    read_value = int(dut.read_data.value)
    print(f"Read address 0x10 again = 0x{read_value:02X}")
    assert read_value == 0xAA, \
        f"Expected 0xAA, got 0x{read_value:02X}"

    print("===================================")
    print("      SIMPLE RAM TEST PASSED       ")
    print("===================================")
