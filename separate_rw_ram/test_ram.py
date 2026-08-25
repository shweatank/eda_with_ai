import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def test_separate_read_write_addresses(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.write_enable.value = 0
    dut.write_address.value = 0
    dut.read_address.value = 0
    dut.write_data.value = 0
    await RisingEdge(dut.clk)

    # Write address 0x10 while reading address 0x20.
    dut.write_enable.value = 1
    dut.write_address.value = 0x10
    dut.read_address.value = 0x20
    dut.write_data.value = 0xA55A
    await RisingEdge(dut.clk)

    dut.write_enable.value = 0
    dut.read_address.value = 0x10
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    actual_value = int(dut.read_data.value)
    print(f"TEST 1: read address 0x10 | expected=0xA55A actual=0x{actual_value:04X}")
    assert actual_value == 0xA55A

    # Write a second address while reading the first address.
    dut.write_enable.value = 1
    dut.write_address.value = 0x20
    dut.read_address.value = 0x10
    dut.write_data.value = 0x5AA5
    await RisingEdge(dut.clk)

    dut.write_enable.value = 0
    dut.read_address.value = 0x20
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    actual_value = int(dut.read_data.value)
    print(f"TEST 2: read address 0x20 | expected=0x5AA5 actual=0x{actual_value:04X}")
    assert actual_value == 0x5AA5

    dut.read_address.value = 0x10
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    actual_value = int(dut.read_data.value)
    print(f"TEST 3: read address 0x10 again | expected=0xA55A actual=0x{actual_value:04X}")
    assert actual_value == 0xA55A

    print("SEPARATE READ/WRITE ADDRESS RAM TEST PASSED")
