import random
import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_edge_cases(dut):
    cases = [(0, 0), (0, 255), (255, 0), (1, 1), (255, 255), (128, 2), (16, 16)]
    for a, b in cases:
        dut.a.value = a
        dut.b.value = b
        await Timer(2, units="ns")

        expected = a * b
        actual = int(dut.y.value)
        assert actual == expected, f"a={a} b={b}: got {actual}, expected {expected}"
        dut._log.info(f"PASS: a={a} b={b} -> y={actual}")


@cocotb.test()
async def test_random(dut):
    errors = 0
    for _ in range(1000):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        dut.a.value = a
        dut.b.value = b
        await Timer(2, units="ns")

        expected = a * b
        actual = int(dut.y.value)
        if actual != expected:
            dut._log.error(f"FAIL: a={a} b={b} -> y={actual} (expected {expected})")
            errors += 1
    assert errors == 0, f"{errors}/1000 mismatch(es) found"