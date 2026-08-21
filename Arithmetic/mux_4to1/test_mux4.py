import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_mux4_select(dut):
    cases = [
        (0b0001, 0b00, 1),
        (0b0010, 0b01, 1),
        (0b0100, 0b10, 1),
        (0b1000, 0b11, 1),
        (0b1010, 0b00, 0),
        (0b1010, 0b01, 1),
        (0b1010, 0b10, 0),
        (0b1010, 0b11, 1),
    ]

    for d, sel, expected in cases:
        dut.d.value = d
        dut.sel.value = sel
        await Timer(1, unit="ns")

        got = int(dut.y.value)
        selected_bit = (d >> sel) & 1
        print(
            f"PASS: d={d:04b}, sel={sel:02b} -> y={got} "
            f"(expected d[{sel}]={selected_bit})"
        )
        assert got == expected
