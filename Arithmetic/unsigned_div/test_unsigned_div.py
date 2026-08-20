import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_unsigned_div(dut):
    vectors = [
        (8, 0, 0, 8),
        (15, 3, 5, 0),
        (255, 5, 51, 0),
        (100, 25, 4, 0),
        (17, 3, 5, 2)
    ]

    for a_val, b_val, q_expected, r_expected in vectors:
        dut.a.value = a_val
        dut.b.value = b_val
        await Timer(1, unit="ns")

        got_q = int(dut.quotient.value)
        got_r = int(dut.remainder.value)

        assert got_q == q_expected, f"FAIL quotient: {a_val} / {b_val} = {got_q}, expected {q_expected}"
        assert got_r == r_expected, f"FAIL remainder: {a_val} % {b_val} = {got_r}, expected {r_expected}"
        print(f"PASS: {a_val} / {b_val} = {got_q}, remainder {got_r}")
