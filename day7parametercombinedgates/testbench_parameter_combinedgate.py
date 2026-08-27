"""Cocotb testbench for vector_gates_combined.

This module does both things at once:
  - every gate's result (y_and, y_or, y_xor, y_nand, y_nor, y_xnor,
    y_not_a, y_not_b) is always computed and available, regardless
    of `sel`
  - y_sel picks out exactly one of those results based on `sel`

Each test drives a/b (and sel where relevant), waits for the
combinational logic to settle, then checks every y_* output AND
y_sel together.
"""

import cocotb
from cocotb.triggers import Timer

WIDTH = 8
MASK = (1 << WIDTH) - 1

GATE_AND = 0
GATE_OR = 1
GATE_XOR = 2
GATE_NAND = 3
GATE_NOR = 4
GATE_XNOR = 5
GATE_NOT_A = 6
GATE_NOT_B = 7

GATE_NAMES = {
    GATE_AND: "AND",
    GATE_OR: "OR",
    GATE_XOR: "XOR",
    GATE_NAND: "NAND",
    GATE_NOR: "NOR",
    GATE_XNOR: "XNOR",
    GATE_NOT_A: "NOT_A",
    GATE_NOT_B: "NOT_B",
}

SIGNAL_FOR_SEL = {
    GATE_AND: "y_and",
    GATE_OR: "y_or",
    GATE_XOR: "y_xor",
    GATE_NAND: "y_nand",
    GATE_NOR: "y_nor",
    GATE_XNOR: "y_xnor",
    GATE_NOT_A: "y_not_a",
    GATE_NOT_B: "y_not_b",
}


def expected_outputs(a, b):
    """Expected value of every always-on gate output for given a, b."""
    return {
        "y_and":   a & b,
        "y_or":    a | b,
        "y_xor":   a ^ b,
        "y_nand":  ~(a & b) & MASK,
        "y_nor":   ~(a | b) & MASK,
        "y_xnor":  ~(a ^ b) & MASK,
        "y_not_a": ~a & MASK,
        "y_not_b": ~b & MASK,
    }


async def check_all_gates(dut, a, b, label):
    """Drive a/b, settle, and assert every y_* output is correct."""
    dut.a.value = a
    dut.b.value = b
    await Timer(1, unit="ns")

    expected = expected_outputs(a, b)
    for signal_name, expected_value in expected.items():
        actual_value = int(getattr(dut, signal_name).value)
        assert actual_value == expected_value, (
            f"{label}: {signal_name} expected 0x{expected_value:02X}, "
            f"got 0x{actual_value:02X} (a=0x{a:02X}, b=0x{b:02X})"
        )
    dut._log.info(
        f"{label}: a=0x{a:02X} b=0x{b:02X} -> "
        + ", ".join(f"{k}=0x{v:02X}" for k, v in expected.items())
    )


async def check_sel(dut, sel, a, b):
    """Drive a/b/sel, settle, and assert y_sel matches the selected gate."""
    dut.a.value = a
    dut.b.value = b
    dut.sel.value = sel
    await Timer(1, unit="ns")

    expected_all = expected_outputs(a, b)
    signal_name = SIGNAL_FOR_SEL[sel]
    expected = expected_all[signal_name]
    actual = int(dut.y_sel.value)
    name = GATE_NAMES[sel]
    assert actual == expected, (
        f"y_sel with sel={name}: expected 0x{expected:02X}, "
        f"got 0x{actual:02X} (a=0x{a:02X}, b=0x{b:02X})"
    )
    return expected_all, signal_name, actual


@cocotb.test()
async def test_all_gates_always_present(dut):
    """Every y_* output should be correct regardless of what sel is set to."""
    dut.sel.value = GATE_AND  # sel shouldn't matter for the y_* outputs

    vectors = [
        (0b10101010, 0b11001100, "Test 1: alternating patterns"),
        (0xFF, 0x0F, "Test 2: full-width vs nibble"),
        (0x00, 0xFF, "Test 3: all zeros vs all ones"),
        (0xFF, 0xFF, "Test 4: all ones vs all ones"),
        (0x00, 0x00, "Test 5: all zeros vs all zeros"),
        (0x5A, 0xA5, "Test 6: exact bitwise complements"),
    ]

    for a, b, label in vectors:
        await check_all_gates(dut, a, b, label)
        dut._log.info(f"{label} PASSED")

    dut._log.info("All gate outputs verified independent of sel")


@cocotb.test()
async def test_sel_matches_corresponding_all_gates_output(dut):
    """y_sel should equal whichever y_* signal `sel` names, for every gate
    and several a/b vectors -- and the OTHER y_* outputs should still be
    correct at the same time (both cases working together)."""
    vectors = [
        (0xFF, 0x0F),
        (0x00, 0xFF),
        (0xFF, 0xFF),
        (0x00, 0x00),
        (0x5A, 0xA5),
        (0b10101010, 0b11001100),
    ]

    for sel in range(8):
        for a, b in vectors:
            expected_all, signal_name, actual = await check_sel(dut, sel, a, b)

            # y_sel matched -- now also confirm every other y_* output
            # is still correct on the exact same cycle.
            for other_name, other_expected in expected_all.items():
                other_actual = int(getattr(dut, other_name).value)
                assert other_actual == other_expected, (
                    f"While sel={GATE_NAMES[sel]}: {other_name} expected "
                    f"0x{other_expected:02X}, got 0x{other_actual:02X}"
                )

            dut._log.info(
                f"sel={GATE_NAMES[sel]} ({signal_name}) -> "
                f"y_sel=0x{actual:02X}, all other outputs also correct"
            )

    dut._log.info("=" * 46)
    dut._log.info("  ALL-GATES + SEL COMBINED TESTS PASSED")
    dut._log.info("=" * 46)