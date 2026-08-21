import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_decoder_2to4(dut):
    """Test 2-to-4 decoder: one-hot output for each 2-bit input"""

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
            f"FAIL: a={a:02b}, got={got:04b}, expected={expected:04b}"
        )
        print(f"PASS: a={a:02b} -> y={got:04b}")