import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_mux(dut):
	
	dut.a.value=0;
	dut.b.value=0;
	await Timer(1,units="ns");
	assert dut.sum.value==0;
	assert dut.carry.value==0;
	
	dut.a.value=0;
	dut.b.value=1;
	await Timer(1,units="ns");
	assert dut.sum.value==1;
	assert dut.carry.value==0;
	
	dut.a.value=1;
	dut.b.value=0;
	await Timer(1,units="ns");
	assert dut.sum.value==1;
	assert dut.carry.value==0;
	
	dut.a.value=1;
	dut.b.value=1;
	await Timer(1,units="ns");
	assert dut.sum.value==0;
	assert dut.carry.value==1;
	
