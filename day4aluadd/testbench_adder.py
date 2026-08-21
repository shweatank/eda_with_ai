import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_adder(dut):
    """Test 8-bit adder: y = A + B"""

    # Try a few representative cases
    test_vectors = [
        (0, 0, 0),
        (5, 10, 15),
        (100, 27, 127),
        (200, 55, 255),   # max 8-bit value
        (255, 1, 0),      # overflow wraps around in 8 bits
    ]

    for A, B, expected in test_vectors:
        dut.A.value = A
        dut.B.value = B
        await Timer(1, units="ns")

        got = int(dut.y.value)
        assert got == expected, f"FAIL: A={A}, B={B}, got {got}, expected {expected}"
        print(f"PASS: A={A}, B={B} → y={got}")