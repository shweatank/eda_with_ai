import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_half_adder(dut):

	#Test A =0 and B=0
	dut.a.value=0;
	dut.b.value=0;
	await Timer(1,units="ns");
	assert dut.y.value==1;
	print("PASS");
	
	#Test A =0 and B=1
	dut.a.value=0;
	dut.b.value=1;
	await Timer(1,units="ns");
	assert dut.y.value==0;
	print("PASS");
	
		
	#Test A =1 and B=0
	dut.a.value=1;
	dut.b.value=0;
	await Timer(1,units="ns");
	assert dut.y.value==0;
	print("PASS");
	
	
		
	#Test A =1 and B=1
	dut.a.value=1;
	dut.b.value=1;
	await Timer(1,units="ns");
	assert dut.y.value==1;
	print("PASS");
	
	
	
	

