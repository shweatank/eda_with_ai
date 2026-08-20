import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_logic_or_and(dut):
    """Test y = (A & B) | C"""
    for A in [0, 1]:
        for B in [0, 1]:
            for C in [0, 1]:
                dut.A.value = A
                dut.B.value = B
                dut.C.value = C
                await Timer(1, units="ns")
                expected = (A & B) | C
                assert dut.y.value == expected, (
                    f"FAIL: A={A}, B={B}, C={C}, "
                    f"got {dut.y.value}, expected {expected}"
                )
                print(f"PASS: A={A}, B={B}, C={C} → y={expected}")