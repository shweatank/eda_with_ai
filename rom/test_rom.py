import cocotb
from cocotb.triggers import Timer


EXPECTED_VALUES = [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88]


@cocotb.test()
async def test_rom_all_addresses(dut):
    for address, expected_value in enumerate(EXPECTED_VALUES):
        dut.address.value = address
        await Timer(1, unit="ns")
        actual_value = int(dut.data.value)
        print(
            f"TEST {address + 1}: address=0x{address:X} | "
            f"expected=0x{expected_value:02X} actual=0x{actual_value:02X}"
        )
        assert actual_value == expected_value, (
            f"Address 0x{address:X}: expected 0x{expected_value:02X}, "
            f"got 0x{actual_value:02X}"
        )

    print("SIMPLE ROM TEST PASSED")
