import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_adder_signed(dut):
    """Test 8-bit signed adder: y = A + B (two's complement, -128..127)"""

    # Try a few representative cases, including negatives and overflow
    test_vectors = [
        (0, 0, 0),
        (5, 10, 15),
        (-5, -10, -15),
        (100, 27, 127),
        (-100, -27, -127),
        (-1, 1, 0),
        (127, 1, -128),      # positive overflow wraps to most-negative
        (-128, -1, 127),     # negative overflow wraps to most-positive
        (-128, -128, 0),     # wraps: -256 mod 256 -> 0
    ]

    for A, B, expected in test_vectors:
        dut.A.value = A
        dut.B.value = B
        await Timer(1, units="ns")

        got = dut.y.value.signed_integer
        assert got == expected, f"FAIL: A={A}, B={B}, got {got}, expected {expected}"
        print(f"PASS: A={A}, B={B} → y={got}")