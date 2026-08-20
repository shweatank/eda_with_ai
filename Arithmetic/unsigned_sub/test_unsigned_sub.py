import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_unsigned_sub(dut):
    vectors = [
        (8, 3, 5),
        (0, 0, 0),
        (255, 1, 254),
        (100, 50, 50),
        (15, 15, 0)
    ]

    for a_val, b_val, expected in vectors:
        dut.a.value = a_val
        dut.b.value = b_val
        await Timer(1, unit="ns")

        got = int(dut.diff.value)
        assert got == expected, f"FAIL: {a_val} - {b_val} = {got}, expected {expected}"
        print(f"PASS: {a_val} - {b_val} = {expected}")
