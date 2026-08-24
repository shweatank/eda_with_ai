import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_half_adder(dut):
    """Exhaustive test for 4-bit half adder"""
    for a in range(16):       # 0–15
        for b in range(16):   # 0–15
            dut.a.value = a
            dut.b.value = b
            await Timer(1, unit="ns")

            expected_sum = a ^ b
            expected_carry = a & b

            got_sum = dut.sum.value.integer
            got_carry = dut.carry.value.integer

            assert got_sum == expected_sum, f"Sum mismatch: a={a}, b={b}, got={got_sum}, expected={expected_sum}"
            assert got_carry == expected_carry, f"Carry mismatch: a={a}, b={b}, got={got_carry}, expected={expected_carry}"
