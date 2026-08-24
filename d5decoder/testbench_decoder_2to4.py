import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_decoder_2to4(dut):
    """Test all input combinations of a 2-to-4 decoder."""

    expected_map = {
        0b00: 0b0001,
        0b01: 0b0010,
        0b10: 0b0100,
        0b11: 0b1000,
    }

    for a in range(4):

        dut.a.value = a

        await Timer(1, units="ns")

        expected = expected_map[a]

        got = int(dut.y.value)

        assert got == expected, (
            f"FAIL: a={a:02b}, "
            f"got={got:04b}, "
            f"expected={expected:04b}"
        )

        print(
            f"PASS: a={a:02b} "
            f"-> y={got:04b}"
        )