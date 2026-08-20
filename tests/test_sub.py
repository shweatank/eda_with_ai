import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def four_ALU(dut):

    boundary_cases = [
        (7, 0, 7),
        (-8, 0, -8),
        (0, 7, -7),
        (7, 7, 0),
        (-8, -8, 0),
    ]

    for a, b, expected in boundary_cases:

        dut.a.value = a
        dut.b.value = b

        await Timer(1, units="ns")

        actual = dut.dif.value.signed_integer

        assert actual == expected, (
            f"Boundary case failed: "
            f"a={a}, b={b}, "
            f"expected={expected}, actual={actual}"
        )
