import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def tes_divide(dut):
	normal_cases = [(10, 2, 5),(12, 3, 4),(15, 5, 3)]
	boundary_cases = [(0, 1, 0),(1, 1, 1),(15, 1, 15),(15, 15, 1)]
	invalid_cases = [(0, 0, 0),(1, 0, 0),(5, 0, 0),(15, 0, 0)]
	
	for a ,b,expected in normal_cases:
		dut.a.value=a
		dut.b.value=b
		await Timer(1,units="ns")
		actual = int(dut.res.value)
		assert actual == expected
		print(f"Normal case: a={a}, b={b}, expected={expected}, actual={actual}")
		
	for a ,b,expected in boundary_cases:
		dut.a.value=a
		dut.b.value=b
		await Timer(1,units="ns")
		actual = int(dut.res.value)
		assert actual == expected
		print(f"boundary case: a={a}, b={b}, expected={expected}, actual={actual}")
		
	for a ,b,expected in invalid_cases:
		dut.a.value=a
		dut.b.value=b
		await Timer(1,units="ns")
		actual = int(dut.res.value)
		assert actual == expected
		print(f"invalid case: a={a}, b={b}, expected={expected}, actual={actual}")	

