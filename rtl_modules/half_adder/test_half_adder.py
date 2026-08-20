"""Cocotb testbench for half adder."""
import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_half_adder_all_cases(dut):
    for a in range(2):
        for b in range(2):
            dut.a.value = a
            dut.b.value = b
            await Timer(2, units="ns")
            expected_sum = a ^ b
            expected_cout = a & b
            assert dut.sum.value == expected_sum
            assert dut.cout.value == expected_cout
