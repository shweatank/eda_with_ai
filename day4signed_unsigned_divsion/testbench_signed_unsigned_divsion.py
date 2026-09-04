import cocotb
from cocotb.triggers import Timer


def trunc_div_mod(A, B):
    """Truncating division/modulo matching Verilog signed '/' and '%'
    (truncate toward zero, remainder takes the sign of the dividend A),
    unlike Python's // and % which floor toward negative infinity.
    """
    q_mag = abs(A) // abs(B)
    q = -q_mag if (A < 0) ^ (B < 0) else q_mag
    r = A - q * B
    return q, r


async def check_unsigned(dut, A_sig, B_sig, q_sig, r_sig, label="unsigned"):
    vectors = [
        (0, 5),
        (10, 3),
        (255, 1),
        (255, 255),
        (100, 7),
        (7, 100),
        (200, 3),
        (0, 0),      # divide by zero -> guarded to 0
        (50, 0),     # divide by zero -> guarded to 0
    ]
    for A, B in vectors:
        A_sig.value = A
        B_sig.value = B
        await Timer(1, units="ns")

        expected_q, expected_r = (0, 0) if B == 0 else (A // B, A % B)
        got_q = int(q_sig.value)
        got_r = int(r_sig.value)

        assert got_q == expected_q, (
            f"FAIL {label} quotient: A={A}, B={B}, got {got_q}, expected {expected_q}"
        )
        assert got_r == expected_r, (
            f"FAIL {label} remainder: A={A}, B={B}, got {got_r}, expected {expected_r}"
        )
        print(f"PASS ({label}): A={A}, B={B} -> quotient={got_q}, remainder={got_r}")


async def check_signed(dut, A_sig, B_sig, q_sig, r_sig, label="signed"):
    vectors = [
        (0, 5),
        (10, 3),
        (-10, 3),
        (10, -3),
        (-10, -3),
        (127, 1),
        (-128, 1),
        (-128, -1),   # overflow case, check 8-bit wraparound
        (7, 100),
        (-7, 100),
        (0, 0),       # divide by zero -> guarded to 0
        (50, 0),      # divide by zero -> guarded to 0
    ]
    for A, B in vectors:
        A_sig.value = A
        B_sig.value = B
        await Timer(1, units="ns")

        if B == 0:
            expected_q, expected_r = 0, 0
        else:
            expected_q, expected_r = trunc_div_mod(A, B)
            # Emulate 8-bit signed wraparound on the quotient, same as hardware
            expected_q = ((expected_q + 128) % 256) - 128

        got_q = q_sig.value.signed_integer
        got_r = r_sig.value.signed_integer

        assert got_q == expected_q, (
            f"FAIL {label} quotient: A={A}, B={B}, got {got_q}, expected {expected_q}"
        )
        assert got_r == expected_r, (
            f"FAIL {label} remainder: A={A}, B={B}, got {got_r}, expected {expected_r}"
        )
        print(f"PASS ({label}): A={A}, B={B} -> quotient={got_q}, remainder={got_r}")


@cocotb.test()
async def test_divider(dut):
    """Single dispatching test — runs the correct logic based on which
    top-level module (divider_unsigned / divider_signed / divider_top)
    was loaded for this simulation."""

    name = dut._name

    if name == "divider_unsigned":
        await check_unsigned(dut, dut.A, dut.B, dut.quotient, dut.remainder)

    elif name == "divider_signed":
        await check_signed(dut, dut.A, dut.B, dut.quotient, dut.remainder)

    elif name == "divider_top":
        await check_unsigned(dut, dut.A_u, dut.B_u, dut.quotient_u, dut.remainder_u, label="unsigned")
        await check_signed(dut, dut.A_s, dut.B_s, dut.quotient_s, dut.remainder_s, label="signed")

    else:
        raise ValueError(f"No test defined for DUT module '{name}'")