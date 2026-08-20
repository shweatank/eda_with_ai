import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_unsigned_mul(dut):
    vectors = [
        (0, 0, 0),
        (1, 1, 1),
        (8, 9, 72),
        (10, 20, 200),
        (255, 2, 510),
        (16, 16, 256)
    ]

    for a_val, b_val, expected in vectors:
        dut.a.value = a_val
        dut.b.value = b_val
        await Timer(1, unit="ns")

        got = int(dut.product.value)
        assert got == expected, f"FAIL: {a_val} * {b_val} = {got}, expected {expected}"
        print(f"PASS: {a_val} * {b_val} = {expected}")
