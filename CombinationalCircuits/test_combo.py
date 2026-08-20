import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_combo_logic(dut):
    """Test all 8 truth table combinations for y = (a & b) | c"""
    
    # Truth table test cases: (a, b, c, expected_y)
    test_cases = [
        (0, 0, 0, 0),
        (0, 0, 1, 1),
        (0, 1, 0, 0),
        (0, 1, 1, 1),
        (1, 0, 0, 0),
        (1, 0, 1, 1),
        (1, 1, 0, 1),
        (1, 1, 1, 1)
    ]

    for a, b, c, expected in test_cases:
        dut.a.value = a
        dut.b.value = b
        dut.c.value = c
        await Timer(1, unit="ns")
        
        # Cast value using int() for Cocotb v2.0 compatibility
        actual = int(dut.y.value)
        assert actual == expected, f"Failed for a={a}, b={b}, c={c}: Expected {expected}, got {actual}"

    print("ALL COMBINATIONAL LOGIC TESTS PASSED SUCCESSFULLY!")