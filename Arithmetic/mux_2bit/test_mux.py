import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_mux_select(dut):
	for a, b in ((0, 0), (0, 1), (1, 0), (1, 1)):
		dut.a.value = a
		dut.b.value = b

		dut.sel.value = 0
		await Timer(1, unit="ns")
		got = int(dut.y.value)
		print(f"PASS: a={a}, b={b}, sel=0 -> y={got} (expected a={a})")
		assert got == a

		dut.sel.value = 1
		await Timer(1, unit="ns")
		got = int(dut.y.value)
		print(f"PASS: a={a}, b={b}, sel=1 -> y={got} (expected b={b})")
		assert got == b
