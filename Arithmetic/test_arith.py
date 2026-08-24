import cocotb
import os
from cocotb.triggers import Timer

def to_signed(val, width):
    """Convert Python int to signed value of given width."""
    mask = (1 << width) - 1
    val &= mask
    if val & (1 << (width - 1)):
        return val - (1 << width)
    return val

@cocotb.test()
async def test_arith(dut):
    width_in = len(dut.a)       # input width (e.g. 4)
    width_out = len(dut.y)      # output width (e.g. 8)

    min_val = -(2 ** (width_in - 1))
    max_val = (2 ** (width_in - 1)) - 1

    # Get OP from environment (passed via Makefile)
    OP = int(os.getenv("OP", "0"))

    # Drive OP into the DUT
    dut.op.value = OP

    for a in range(min_val, max_val + 1):
        for b in range(min_val, max_val + 1):
            dut.a.value = a
            dut.b.value = b
            await Timer(1, unit="ns")   # updated keyword: unit not units

            # Compute expected result in Python
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
            else:
                expected = 0

            # Normalize expected to output width
            expected = to_signed(expected, width_out)

            # Get DUT output using new API
            try:
                got = dut.y.value.to_signed()
            except AttributeError:
                raw = int(dut.y.value)
                got = raw - (1 << width_out) if raw >= (1 << (width_out - 1)) else raw

            # Compare with detailed error message
            assert got == expected, (
                f"FAIL: OP={OP}, a={a}, b={b}\n"
                f"  Expected: {expected} (0x{expected & ((1<<width_out)-1):02X})\n"
                f"  Got: {got} (0x{int(dut.y.value):02X})"
            )
