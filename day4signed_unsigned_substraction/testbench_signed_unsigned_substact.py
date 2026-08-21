import cocotb
from cocotb.triggers import Timer


async def check_unsigned(dut, A_sig, B_sig, y_sig, label="unsigned"):
    vectors = [
        (10, 5),
        (5, 10),      # underflow: wraps around (5 - 10 = -5 -> 251 in 8-bit unsigned)
        (0, 0),
        (0, 1),       # underflow: 0 - 1 -> 255
        (255, 255),
        (255, 0),
        (100, 100),
        (200, 50),
    ]
    for A, B in vectors:
        A_sig.value = A
        B_sig.value = B
        await Timer(1, units="ns")

        expected = (A - B) % 256  # unsigned wraparound behavior
        got = int(y_sig.value)

        assert got == expected, (
            f"FAIL {label}: A={A}, B={B}, got {got}, expected {expected}"
        )
        print(f"PASS ({label}): A={A}, B={B} -> y={got}")


async def check_signed(dut, A_sig, B_sig, y_sig, label="signed"):
    vectors = [
        (10, 5),
        (5, 10),
        (-10, 5),
        (10, -5),
        (-10, -5),
        (0, 0),
        (-128, 1),    # overflow: -129 doesn't fit, wraps to 127
        (127, -1),    # overflow: 128 doesn't fit, wraps to -128
        (-128, -128), # 0
    ]
    for A, B in vectors:
        A_sig.value = A
        B_sig.value = B
        await Timer(1, units="ns")

        raw = A - B
        expected = ((raw + 128) % 256) - 128  # 8-bit signed wraparound

        got = y_sig.value.signed_integer

        assert got == expected, (
            f"FAIL {label}: A={A}, B={B}, got {got}, expected {expected}"
        )
        print(f"PASS ({label}): A={A}, B={B} -> y={got}")


@cocotb.test()
async def test_subtractor(dut):
    """Single dispatching test — runs the correct logic based on which
    top-level module (subtractor_unsigned / subtractor_signed / subtractor_top)
    was loaded for this simulation."""

    name = dut._name

    if name == "subtractor_unsigned":
        await check_unsigned(dut, dut.A, dut.B, dut.y)

    elif name == "subtractor_signed":
        await check_signed(dut, dut.A, dut.B, dut.y)

    elif name == "subtractor_top":
        await check_unsigned(dut, dut.A_u, dut.B_u, dut.y_u, label="unsigned")
        await check_signed(dut, dut.A_s, dut.B_s, dut.y_s, label="signed")

    else:
        raise ValueError(f"No test defined for DUT module '{name}'")