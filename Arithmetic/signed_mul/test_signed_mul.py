import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_signed_mul(dut):
    vectors = [
        (-1, -1, 1),
        (-5, 3, -15),
        (8, 9, 72),
        (-8, -9, 72),
        (127, 2, 254),
        (-128, -1, 128)
    ]

    for a_val, b_val, expected in vectors:
        dut.a.value = a_val
        dut.b.value = b_val
        await Timer(1, unit="ns")

        got = int(dut.product.value.signed_integer)
        assert got == expected, f"FAIL: {a_val} * {b_val} = {got}, expected {expected}"
        print(f"PASS: {a_val} * {b_val} = {expected}")
