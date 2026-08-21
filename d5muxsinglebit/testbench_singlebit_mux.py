import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_mux_singlebit(dut):
    """Test 2:1 Multiplexer: sel=0 -> y=a, sel=1 -> y=b"""

    for a in [0, 1]:
        for b in [0, 1]:
            for sel in [0, 1]:
                dut.a.value = a
                dut.b.value = b
                dut.sel.value = sel
                await Timer(1, units="ns")

                expected = b if sel else a
                got = int(dut.y.value)

                assert got == expected, (
                    f"FAIL: a={a}, b={b}, sel={sel}, got={got}, expected={expected}"
                )
                print(f"PASS: a={a}, b={b}, sel={sel} -> y={got}")