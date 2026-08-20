import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_add(dut):
    for a in range(-128 ,128):
        for b in range(-128, 128):
            dut.a.value = a
            dut.b.value = b
            await Timer(1, units="ns")

            expected = a + b
            got = dut.y.value.signed_integer   # signed interpretation

            assert got == expected, f"FAIL: a={a}, b={b}, expected={expected}, got={got}"
            print(f"PASS: a={a}, b={b}, y={got}")
