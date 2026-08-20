import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_signed_sub(dut):
    vectors = [
        (-1, 1, -2),
        (0, 0, 0),
        (10, 5, 5),
        (-10, -5, -5),
        (127, -1, 128),
        (-128, -1, -127)
    ]

    for a_val, b_val, expected in vectors:
        dut.a.value = a_val
        dut.b.value = b_val
        await Timer(1, unit="ns")

        got = int(dut.diff.value.signed_integer)
        assert got == expected, f"FAIL: {a_val} - {b_val} = {got}, expected {expected}"
        print(f"PASS: {a_val} - {b_val} = {expected}")
