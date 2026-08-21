import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_comparator(dut):
    """Test 8-bit unsigned comparator: equal, greater, less"""

    vectors = [
        (0, 0),
        (5, 5),
        (10, 5),
        (5, 10),
        (255, 0),
        (0, 255),
        (255, 255),
        (127, 128),
    ]

    for a, b in vectors:
        dut.a.value = a
        dut.b.value = b
        await Timer(1, units="ns")

        expected_equal = int(a == b)
        expected_greater = int(a > b)
        expected_less = int(a < b)

        got_equal = int(dut.equal.value)
        got_greater = int(dut.greater.value)
        got_less = int(dut.less.value)

        assert got_equal == expected_equal, (
            f"FAIL equal: a={a}, b={b}, got={got_equal}, expected={expected_equal}"
        )
        assert got_greater == expected_greater, (
            f"FAIL greater: a={a}, b={b}, got={got_greater}, expected={expected_greater}"
        )
        assert got_less == expected_less, (
            f"FAIL less: a={a}, b={b}, got={got_less}, expected={expected_less}"
        )

        print(
            f"PASS: a={a}, b={b} -> equal={got_equal}, greater={got_greater}, less={got_less}"
        )
