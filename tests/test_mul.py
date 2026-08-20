import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_multiplier(dut):

    normal_cases = [
        (2, 3, 6),
        (4, 5, 20),
        (6, 7, 42),
        (8, 3, 24),
        (10, 5, 50),
        (12, 4, 48)
    ]

    boundary_cases = [
        (0, 0, 0),
        (0, 15, 0),
        (15, 0, 0),
        (1, 1, 1),
        (1, 15, 15),
        (15, 1, 15),
        (15, 15, 225)
    ]

    for a, b, expected in normal_cases:

        dut.a.value = a
        dut.b.value = b

        await Timer(1, units="ns")

        actual = int(dut.res.value)

        assert actual == expected

        print(
            f"Normal case: a={a}, b={b}, "
            f"expected={expected}, actual={actual}"
        )

    for a, b, expected in boundary_cases:

        dut.a.value = a
        dut.b.value = b

        await Timer(1, units="ns")

        actual = int(dut.res.value)

        assert actual == expected

        print(
            f"Boundary case: a={a}, b={b}, "
            f"expected={expected}, actual={actual}"
        )
