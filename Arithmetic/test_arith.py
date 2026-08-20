import cocotb
import os
from cocotb.triggers import Timer

@cocotb.test()
async def test_arith(dut):
    width = len(dut.a)
    min_val = -(2**(width-1))
    max_val = (2**(width-1)) - 1

    # Get OP from environment (passed via Makefile)
    OP = int(os.getenv("OP", "0"))

    for a in range(min_val, max_val+1):
        for b in range(min_val, max_val+1):
            dut.a.value = a
            dut.b.value = b
            await Timer(1, units="ns")

            if OP == 0:   # ADD
                expected = a + b
            elif OP == 1: # SUB
                expected = a - b
            elif OP == 2: # MUL
                expected = a * b
            elif OP == 3: # DIV
                expected = int(a / b) if b != 0 else 0
            elif OP == 4: # MOD
                expected = a % b if b != 0 else 0
            elif OP == 5: # PASS A
                expected = a
            elif OP == 6: # PASS B
                expected = b
            elif OP == 7: # CLEAR
                expected = 0

            got = dut.y.value.signed_integer
            assert got == expected, f"FAIL: OP={OP}, a={a}, b={b}, expected={expected}, got={got}"