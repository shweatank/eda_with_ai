import cocotb
from cocotb.triggers import RisingEdge
import random

@cocotb.test()
async def ram_test(dut):
    for i in range(8):
        val = random.randint(0,255)
        dut.we.value = 1
        dut.addr.value = i
        dut.din.value = val
        await RisingEdge(dut.clk)
        dut.we.value = 0
        await RisingEdge(dut.clk)
        assert dut.dout.value == val, f"Mismatch at addr {i}"
