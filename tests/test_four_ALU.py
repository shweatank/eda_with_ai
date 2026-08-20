import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def four_ALU(dut):

    for i in rang(-8,8):
        for j in range(-8,8):

            dut.a.value = i
            dut.b.value = j

            await Timer(1, units="ns")

            expected = (i + j) & 0xF
            actual = int(dut.sum.value)

            print(
                f"a={i}, b={j}, expected={expected}, actual={actual}"
            )

            assert actual == expected, (
                f"ALU failed: a={i}, b={j}, "
                f"expected={expected}, actual={actual}"
            )
