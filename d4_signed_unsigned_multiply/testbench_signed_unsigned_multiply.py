import cocotb
from cocotb.triggers import Timer


async def check_unsigned(dut, A_sig, B_sig, prod_sig, label="unsigned"):
    vectors = [
        (0, 0),
        (0, 255),
        (1, 1),
        (10, 5),
        (255, 255),   # max magnitude, verifies full 16-bit width is used
        (100, 100),
        (16, 16),
        (7, 200),
    ]
    for A, B in vectors:
        A_sig.value = A
        B_sig.value = B
        await Timer(1, units="ns")

        expected = A * B
        got = int(prod_sig.value)

        assert got == expected, (
            f"FAIL {label} product: A={A}, B={B}, got {got}, expected {expected}"
        )
        print(f"PASS ({label}): A={A}, B={B} -> product={got}")


async def check_signed(dut, A_sig, B_sig, prod_sig, label="signed"):
    vectors = [
        (0, 0),
        (1, 1),
        (10, 5),
        (-10, 5),
        (10, -5),
        (-10, -5),
        (127, 127),     # max positive x max positive
        (-128, 127),    # min negative x max positive
        (-128, -128),   # min negative x min negative, largest magnitude product
        (-1, -1),
    ]
    for A, B in vectors:
        A_sig.value = A
        B_sig.value = B
        await Timer(1, units="ns")

        expected = A * B  # fits safely in 16-bit signed range, no wraparound needed
        got = prod_sig.value.signed_integer

        assert got == expected, (
            f"FAIL {label} product: A={A}, B={B}, got {got}, expected {expected}"
        )
        print(f"PASS ({label}): A={A}, B={B} -> product={got}")


@cocotb.test()
async def test_multiplier(dut):
    """Single dispatching test — runs the correct logic based on which
    top-level module (multiplier_unsigned / multiplier_signed / multiplier_top)
    was loaded for this simulation."""

    name = dut._name

    if name == "multiplier_unsigned":
        await check_unsigned(dut, dut.A, dut.B, dut.product)

    elif name == "multiplier_signed":
        await check_signed(dut, dut.A, dut.B, dut.product)

    elif name == "multiplier_top":
        await check_unsigned(dut, dut.A_u, dut.B_u, dut.product_u, label="unsigned")
        await check_signed(dut, dut.A_s, dut.B_s, dut.product_s, label="signed")

    else:
        raise ValueError(f"No test defined for DUT module '{name}'")