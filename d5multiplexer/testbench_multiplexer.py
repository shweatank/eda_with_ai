import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_mux4(dut):
    """Test 4:1 Multiplexer"""

    d_values = [0b1010, 0b0101]
    for d in d_values:
        dut.d.value = d
        for sel in range(4):
            dut.sel.value = sel
            await Timer(1, units="ns")

            expected = (d >> sel) & 1
            got = int(dut.y.value)
            assert got == expected, f"FAIL: d={d:04b}, sel={sel}, got={got}, expected={expected}"
            print(f"PASS: d={d:04b}, sel={sel} -> y={got}")