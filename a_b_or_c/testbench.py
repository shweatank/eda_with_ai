import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_logic_circuit(dut):

    for A in [0, 1]:
        for B in [0, 1]:
            for C in [0, 1]:

                dut.A.value = A
                dut.B.value = B
                dut.C.value = C

                await Timer(1, units="ns")

                expected = (A & B) | C

                print(
                    f"A={A} B={B} C={C} "
                    f"-> Y={dut.Y.value} "
                    f"(expected={expected})"
                )

                assert dut.Y.value == expected