import random

import cocotb
from cocotb.triggers import Timer

# @cocotb.test()
# async def test_subs(dut):
#     errors = 0
#     for a in range(256):
#         for b in range(256):
#             dut.a.value = a
#             dut.b.value = b
#             await Timer(10, units="ns")
#             expected = a - b
#             actual = int(dut.y.value)
#             if actual != expected:
#                 errors += 1
#                 dut._log.error(f"FAIL: a={a} b={b} -> y={actual} (expected {expected})")
#
#     assert errors == 0, f"{errors} mismatch(es) found in exhaustive test"

import random
import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_edge_cases(dut):
    cases = [(0, 0), (-1, -1), (-1, 1), (-128, -128), (-128, 127), (127, 127), (127, 1), (-50, 50), (0, -1)]
    for a, b in cases:
        dut.a.value = a
        dut.b.value = b
        await Timer(2, units="ns")
        expected = a - b
        actual = dut.y.value.signed_integer   # <-- signed readback, not int()
        assert actual == expected, f"a={a} b={b}: got {actual}, expected {expected}"
        dut._log.info(f"PASS: a={a} b={b} -> y={actual}")


@cocotb.test()
async def test_random(dut):
    errors = 0
    num_tests = 1000
    for _ in range(num_tests):
        a = random.randint(-128, 127)   # <-- signed range, not 0-255
        b = random.randint(-128, 127)
        dut.a.value = a
        dut.b.value = b
        await Timer(2, units="ns")
        expected = a - b
        actual = dut.y.value.signed_integer   # <-- signed readback
        if actual != expected:
            dut._log.error(f"FAIL: a={a} b={b} -> y={actual} (expected {expected})")
            errors += 1
    assert errors == 0, f"{errors}/{num_tests} mismatch(es) found"

@cocotb.test()
async def test_signed_edge_cases(dut):
    """Check specific signed edge cases: extremes, zero-crossing, overflow boundary."""
    cases = [
        (0, 0),
        (-1, -1),
        (-1, 1),
        (-128, -128),   # most negative + most negative
        (-128, 127),    # most negative + most positive
        (127, 127),     # most positive + most positive (needs 9th bit)
        (127, 1),
        (-50, 50),      # cancels to zero
        (0, -1),
    ]

    for a, b in cases:
        dut.a.value = a   # cocotb accepts negative ints directly on signed ports
        dut.b.value = b
        await Timer(2, units="ns")

        expected = a - b
        actual = dut.y.value.signed_integer   # interpret output as signed
        assert actual == expected, f"a={a} b={b}: got {actual}, expected {expected}"
        dut._log.info(f"PASS: a={a} b={b} -> y={actual}")