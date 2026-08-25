import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_rom(dut):

    # Expected ROM contents
    expected_data = [
        0x11,
        0x22,
        0x33,
        0x44,
        0x55,
        0x66,
        0x77,
        0x88
    ]

    # Test all ROM addresses
    for address in range(8):

        # Apply address
        dut.address.value = address

        # Wait for combinational logic to settle
        await Timer(1, units="ns")

        # Read output
        read_value = int(dut.data.value)

        print(
            f"Address = 0x{address:X}, "
            f"Data = 0x{read_value:02X}"
        )

        # Verify
        assert read_value == expected_data[address], \
            f"Address 0x{address:X}: expected 0x{expected_data[address]:02X}, got 0x{read_value:02X}"

    print("===================================")
    print("        ROM TEST PASSED            ")
    print("===================================")
