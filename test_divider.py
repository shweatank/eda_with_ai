import random
import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_edge_cases(dut):
    cases = [
        (10, 2),    # simple case
        (255, 1),   # divide by 1
        (0, 5),     # zero dividend
        (7, 3),     # non-exact division (tests remainder)
        (255, 255), # equal values
        (100, 7),
    ]
    for a, b in cases:
        dut.a.value = a
        dut.b.value = b
        await Timer(2, units="ns")

        expected_q = a // b
        expected_r = a % b
        actual_q = int(dut.quotient.value)
        actual_r = int(dut.remainder.value)

        assert actual_q == expected_q, f"a={a} b={b}: quotient got {actual_q}, expected {expected_q}"
        assert actual_r == expected_r, f"a={a} b={b}: remainder got {actual_r}, expected {expected_r}"
        assert dut.div_by_zero.value == 0, f"a={a} b={b}: div_by_zero should be 0"
        dut._log.info(f"PASS: a={a} b={b} -> q={actual_q} r={actual_r}")


@cocotb.test()
async def test_div_by_zero(dut):
    """Explicitly verify the divide-by-zero flag asserts correctly."""
    dut.a.value = 42
    dut.b.value = 0
    await Timer(2, units="ns")

    assert dut.div_by_zero.value == 1, "div_by_zero flag should assert when b=0"
    dut._log.info("PASS: div_by_zero correctly flagged for b=0")


@cocotb.test()
async def test_random(dut):
    errors = 0
    for _ in range(1000):
        a = random.randint(0, 255)
        b = random.randint(1, 255)  # avoid zero for the main random sweep
        dut.a.value = a
        dut.b.value = b
        await Timer(2, units="ns")

        expected_q = a // b
        expected_r = a % b
        actual_q = int(dut.quotient.value)
        actual_r = int(dut.remainder.value)

        if actual_q != expected_q or actual_r != expected_r:
            dut._log.error(
                f"FAIL: a={a} b={b} -> q={actual_q} (exp {expected_q}), "
                f"r={actual_r} (exp {expected_r})"
            )
            errors += 1
    assert errors == 0, f"{errors}/1000 mismatch(es) found"