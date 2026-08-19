import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_all_gate_combinations(dut):

    test_vectors = [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    ]

    for a, b in test_vectors:

        dut.a.value = a
        dut.b.value = b

        # Allow combinational logic to settle
        await Timer(1, units="ns")

        expected_and = a & b
        expected_or = a | b
        expected_not = (~a) & 1
        expected_nand = (~(a & b)) & 1
        expected_nor = (~(a | b)) & 1
        expected_xor = a ^ b
        expected_xnor = (~(a ^ b)) & 1

        assert dut.and_y.value.integer == expected_and, (
            f"AND failed: a={a}, b={b}"
        )

        assert dut.or_y.value.integer == expected_or, (
            f"OR failed: a={a}, b={b}"
        )

        assert dut.not_y.value.integer == expected_not, (
            f"NOT failed: a={a}, b={b}"
        )

        assert dut.nand_y.value.integer == expected_nand, (
            f"NAND failed: a={a}, b={b}"
        )

        assert dut.nor_y.value.integer == expected_nor, (
            f"NOR failed: a={a}, b={b}"
        )

        assert dut.xor_y.value.integer == expected_xor, (
            f"XOR failed: a={a}, b={b}"
        )

        assert dut.xnor_y.value.integer == expected_xnor, (
            f"XNOR failed: a={a}, b={b}"
        )

        dut._log.info(
            f"PASS: a={a}, b={b} | "
            f"AND={expected_and}, "
            f"OR={expected_or}, "
            f"NOT={expected_not}, "
            f"NAND={expected_nand}, "
            f"NOR={expected_nor}, "
            f"XOR={expected_xor}, "
            f"XNOR={expected_xnor}"
        )

    dut._log.info("ALL GATE TESTS PASSED")