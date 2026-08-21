import cocotb
from cocotb.triggers import Timer


def trunc_div_mod(A, B):
    """Truncating division/modulo matching Verilog signed '/' and '%'
    (truncate toward zero, remainder takes the sign of the dividend A)."""
    q_mag = abs(A) // abs(B)
    q = -q_mag if (A < 0) ^ (B < 0) else q_mag
    r = A - q * B
    return q, r


# ---------------- Addition ----------------

async def check_add_unsigned(dut, A_sig, B_sig, y_sig, label="add_unsigned"):
    vectors = [(0, 0), (5, 10), (100, 27), (200, 55), (255, 1)]
    for A, B in vectors:
        A_sig.value = A
        B_sig.value = B
        await Timer(1, units="ns")
        expected = (A + B) % 256
        got = int(y_sig.value)
        assert got == expected, f"FAIL {label}: A={A}, B={B}, got {got}, expected {expected}"
        print(f"PASS ({label}): A={A}, B={B} -> y={got}")


async def check_add_signed(dut, A_sig, B_sig, y_sig, label="add_signed"):
    vectors = [(0, 0), (5, 10), (-5, -10), (100, 27), (-100, -27), (127, 1), (-128, -1)]
    for A, B in vectors:
        A_sig.value = A
        B_sig.value = B
        await Timer(1, units="ns")
        expected = ((A + B + 128) % 256) - 128
        got = y_sig.value.signed_integer
        assert got == expected, f"FAIL {label}: A={A}, B={B}, got {got}, expected {expected}"
        print(f"PASS ({label}): A={A}, B={B} -> y={got}")


# ---------------- Subtraction ----------------

async def check_sub_unsigned(dut, A_sig, B_sig, y_sig, label="sub_unsigned"):
    vectors = [(10, 5), (5, 10), (0, 1), (255, 0), (200, 50)]
    for A, B in vectors:
        A_sig.value = A
        B_sig.value = B
        await Timer(1, units="ns")
        expected = (A - B) % 256
        got = int(y_sig.value)
        assert got == expected, f"FAIL {label}: A={A}, B={B}, got {got}, expected {expected}"
        print(f"PASS ({label}): A={A}, B={B} -> y={got}")


async def check_sub_signed(dut, A_sig, B_sig, y_sig, label="sub_signed"):
    vectors = [(10, 5), (-10, 5), (10, -5), (0, 0), (-128, 1), (127, -1)]
    for A, B in vectors:
        A_sig.value = A
        B_sig.value = B
        await Timer(1, units="ns")
        expected = ((A - B + 128) % 256) - 128
        got = y_sig.value.signed_integer
        assert got == expected, f"FAIL {label}: A={A}, B={B}, got {got}, expected {expected}"
        print(f"PASS ({label}): A={A}, B={B} -> y={got}")


# ---------------- Multiplication ----------------

async def check_mul_unsigned(dut, A_sig, B_sig, prod_sig, label="mul_unsigned"):
    vectors = [(0, 0), (1, 1), (10, 5), (255, 255), (16, 16)]
    for A, B in vectors:
        A_sig.value = A
        B_sig.value = B
        await Timer(1, units="ns")
        expected = A * B
        got = int(prod_sig.value)
        assert got == expected, f"FAIL {label}: A={A}, B={B}, got {got}, expected {expected}"
        print(f"PASS ({label}): A={A}, B={B} -> product={got}")


async def check_mul_signed(dut, A_sig, B_sig, prod_sig, label="mul_signed"):
    vectors = [(0, 0), (10, 5), (-10, 5), (127, 127), (-128, -128), (-1, -1)]
    for A, B in vectors:
        A_sig.value = A
        B_sig.value = B
        await Timer(1, units="ns")
        expected = A * B
        got = prod_sig.value.signed_integer
        assert got == expected, f"FAIL {label}: A={A}, B={B}, got {got}, expected {expected}"
        print(f"PASS ({label}): A={A}, B={B} -> product={got}")


# ---------------- Division ----------------

async def check_div_unsigned(dut, A_sig, B_sig, q_sig, r_sig, label="div_unsigned"):
    vectors = [(0, 5), (10, 3), (255, 1), (100, 7), (0, 0), (50, 0)]
    for A, B in vectors:
        A_sig.value = A
        B_sig.value = B
        await Timer(1, units="ns")
        expected_q, expected_r = (0, 0) if B == 0 else (A // B, A % B)
        got_q = int(q_sig.value)
        got_r = int(r_sig.value)
        assert got_q == expected_q, f"FAIL {label} quotient: A={A}, B={B}, got {got_q}, expected {expected_q}"
        assert got_r == expected_r, f"FAIL {label} remainder: A={A}, B={B}, got {got_r}, expected {expected_r}"
        print(f"PASS ({label}): A={A}, B={B} -> quotient={got_q}, remainder={got_r}")


async def check_div_signed(dut, A_sig, B_sig, q_sig, r_sig, label="div_signed"):
    vectors = [(0, 5), (-10, 3), (10, -3), (127, 1), (-128, -1), (0, 0), (50, 0)]
    for A, B in vectors:
        A_sig.value = A
        B_sig.value = B
        await Timer(1, units="ns")
        if B == 0:
            expected_q, expected_r = 0, 0
        else:
            expected_q, expected_r = trunc_div_mod(A, B)
            expected_q = ((expected_q + 128) % 256) - 128
        got_q = q_sig.value.signed_integer
        got_r = r_sig.value.signed_integer
        assert got_q == expected_q, f"FAIL {label} quotient: A={A}, B={B}, got {got_q}, expected {expected_q}"
        assert got_r == expected_r, f"FAIL {label} remainder: A={A}, B={B}, got {got_r}, expected {expected_r}"
        print(f"PASS ({label}): A={A}, B={B} -> quotient={got_q}, remainder={got_r}")


# ---------------- Dispatch ----------------

@cocotb.test()
async def test_alu(dut):
    """Single dispatching test — runs the correct logic based on which
    top-level module was loaded for this simulation."""

    name = dut._name

    if name == "adder_unsigned":
        await check_add_unsigned(dut, dut.A, dut.B, dut.y)

    elif name == "adder_signed":
        await check_add_signed(dut, dut.A, dut.B, dut.y)

    elif name == "subtractor_unsigned":
        await check_sub_unsigned(dut, dut.A, dut.B, dut.y)

    elif name == "subtractor_signed":
        await check_sub_signed(dut, dut.A, dut.B, dut.y)

    elif name == "multiplier_unsigned":
        await check_mul_unsigned(dut, dut.A, dut.B, dut.product)

    elif name == "multiplier_signed":
        await check_mul_signed(dut, dut.A, dut.B, dut.product)

    elif name == "divider_unsigned":
        await check_div_unsigned(dut, dut.A, dut.B, dut.quotient, dut.remainder)

    elif name == "divider_signed":
        await check_div_signed(dut, dut.A, dut.B, dut.quotient, dut.remainder)

    elif name == "alu_top":
        await check_add_unsigned(dut, dut.Add_A_u, dut.Add_B_u, dut.Add_Y_u)
        await check_add_signed(dut, dut.Add_A_s, dut.Add_B_s, dut.Add_Y_s)

        await check_sub_unsigned(dut, dut.Sub_A_u, dut.Sub_B_u, dut.Sub_Y_u)
        await check_sub_signed(dut, dut.Sub_A_s, dut.Sub_B_s, dut.Sub_Y_s)

        await check_mul_unsigned(dut, dut.Mul_A_u, dut.Mul_B_u, dut.Mul_Y_u)
        await check_mul_signed(dut, dut.Mul_A_s, dut.Mul_B_s, dut.Mul_Y_s)

        await check_div_unsigned(dut, dut.Div_A_u, dut.Div_B_u, dut.Div_Q_u, dut.Div_R_u)
        await check_div_signed(dut, dut.Div_A_s, dut.Div_B_s, dut.Div_Q_s, dut.Div_R_s)

    else:
        raise ValueError(f"No test defined for DUT module '{name}'")