import random
import cocotb
from cocotb.triggers import Timer


def to_signed(val, bits):
    if val >= (1 << (bits - 1)):
        val -= (1 << bits)
    return val


@cocotb.test()
async def test_edge_cases(dut):
    cases = [(0, 0), (255, 0), (0, 255), (100, 50), (50, 100), (255, 255), (1, 1)]
    for a, b in cases:
        dut.a.value = a
        dut.b.value = b
        await Timer(2, units="ns")

        expected = to_signed((a - b) & 0x1FF, 9)  # wrap into 9-bit two's complement
        actual = to_signed(int(dut.y.value), 9)
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

        expected = to_signed((a - b) & 0x1FF, 9)
        actual = to_signed(int(dut.y.value), 9)
        if actual != expected:
            dut._log.error(f"FAIL: a={a} b={b} -> y={actual} (expected {expected})")
            errors += 1
    assert errors == 0, f"{errors}/1000 mismatch(es) found"