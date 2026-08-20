import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_xnor(dut):

    test_cases = [
        (0, 0, 1),
        (0, 1, 0),
        (1, 0, 0),
        (1, 1, 1),
    ]

    for a, b, expected in test_cases:

        dut.a.value = a
        dut.b.value = b

        await Timer(1, units="ns")

        actual = int(dut.y.value)

        assert actual == expected, (
            f"FAIL: a={a}, b={b}, "
            f"expected={expected}, actual={actual}"
        )

        print(
            f"PASS: a={a}, b={b}, "
            f"y={actual}"
        )