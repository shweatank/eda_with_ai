import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_mux_select(dut):
    cases = [
        (0b000, 0b000),
        (0b001, 0b010),
        (0b101, 0b011),
        (0b111, 0b100),
    ]

    for a, b in cases:
        dut.a.value = a
        dut.b.value = b

        dut.sel.value = 0
        await Timer(1, unit="ns")
        got = int(dut.y.value)
        print(f"PASS: a={a:03b}, b={b:03b}, sel=0 -> y={got:03b} (expected a={a:03b})")
        assert got == a

        dut.sel.value = 1
        await Timer(1, unit="ns")
        got = int(dut.y.value)
        print(f"PASS: a={a:03b}, b={b:03b}, sel=1 -> y={got:03b} (expected b={b:03b})")
        assert got == b