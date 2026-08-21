import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_logic_gates(dut):
    """Test combined AND/OR/NAND/NOR outputs for all input combinations"""

    for a in [0, 1]:
        for b in [0, 1]:
            dut.a.value = a
            dut.b.value = b
            await Timer(1, units="ns")

            expected_and = a & b
            expected_or = a | b
            expected_nand = int(not (a & b))
            expected_nor = int(not (a | b))

            got_and = int(dut.and_out.value)
            got_or = int(dut.or_out.value)
            got_nand = int(dut.nand_out.value)
            got_nor = int(dut.nor_out.value)

            assert got_and == expected_and, (
                f"FAIL and_out: a={a}, b={b}, got={got_and}, expected={expected_and}"
            )
            assert got_or == expected_or, (
                f"FAIL or_out: a={a}, b={b}, got={got_or}, expected={expected_or}"
            )
            assert got_nand == expected_nand, (
                f"FAIL nand_out: a={a}, b={b}, got={got_nand}, expected={expected_nand}"
            )
            assert got_nor == expected_nor, (
                f"FAIL nor_out: a={a}, b={b}, got={got_nor}, expected={expected_nor}"
            )

            print(
                f"PASS: a={a}, b={b} -> and={got_and}, or={got_or}, "
                f"nand={got_nand}, nor={got_nor}"
            )