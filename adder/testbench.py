import cocotb
from cocotb.triggers import Timer


def signed_8bit(value):
    value &= 0xFF

    if value & 0x80:
        return value - 256

    return value


@cocotb.test()
async def test_signed_adder(dut):

    test_cases = [
        (0, 0),
        (10, 20),
        (-10, 5),
        (-10, -5),
        (50, -20),
        (-50, 20),
        (127, 1),       
        (-128, -1),     
        (127, 127),
        (-128, -128),
    ]

    for A, B in test_cases:

        dut.A.value = A & 0xFF
        dut.B.value = B & 0xFF

        await Timer(1, units="ns")

        expected = A + B

        # Expected 8-bit signed result
        expected_sum = signed_8bit(expected)

        # Signed overflow
        expected_overflow = (
            expected < -128 or expected > 127
        )

        actual_sum = signed_8bit(int(dut.Sum.value))
        actual_overflow = int(dut.Overflow.value)

        print(
            f"A={A:4}, B={B:4} "
            f"-> Sum={actual_sum:4}, "
            f"Overflow={actual_overflow}"
        )

        assert actual_sum == expected_sum
        assert actual_overflow == expected_overflow