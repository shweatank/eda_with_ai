import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def test_dynamic_ram(dut):
    data_width = len(dut.write_data)
    data_mask = (1 << data_width) - 1
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.write_enable.value = 0
    dut.address.value = 0
    dut.write_data.value = 0
    await RisingEdge(dut.clk)

    test_words = [(0x10, 0xA5A5A5A5), (0x20, 0x5A5A5A5A), (0xFF, 0x12345678)]
    expected = {}
    for address, value in test_words:
        value &= data_mask
        dut.write_enable.value = 1
        dut.address.value = address
        dut.write_data.value = value
        await RisingEdge(dut.clk)
        expected[address] = value
        print(f"WRITE address=0x{address:02X} data=0x{value:X}")

    dut.write_enable.value = 0
    for address, expected_value in expected.items():
        dut.address.value = address
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        actual_value = int(dut.read_data.value)
        print(f"READ address=0x{address:02X} expected=0x{expected_value:X} actual=0x{actual_value:X}")
        assert actual_value == expected_value

    print(f"DYNAMIC RAM TEST PASSED for DATA_WIDTH={data_width}")
