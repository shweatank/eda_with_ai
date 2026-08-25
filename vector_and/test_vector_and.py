import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_vector_and_all_patterns(dut):
    width = len(dut.a)
    mask = (1 << width) - 1

    test_vectors = [
        (0x00, 0x00),
        (0xFF, 0x00),
        (0xFF, 0xFF),
        (0xAA, 0x55),
        (0x0F, 0xF0),
        (0x3C, 0xA5),
    ]

    for a_value, b_value in test_vectors:
        a_value &= mask
        b_value &= mask
        dut.a.value = a_value
        dut.b.value = b_value
        await Timer(1, unit="ns")

        actual_value = int(dut.y.value)
        expected_value = a_value & b_value
        print(
            f"a=0x{a_value:02X} b=0x{b_value:02X} "
            f"expected=0x{expected_value:02X} actual=0x{actual_value:02X}"
        )
        assert actual_value == expected_value, (
            f"a=0x{a_value:02X}, b=0x{b_value:02X}: "
            f"expected 0x{expected_value:02X}, got 0x{actual_value:02X}"
        )

    print(f"VECTOR AND TEST PASSED for WIDTH={width}")
