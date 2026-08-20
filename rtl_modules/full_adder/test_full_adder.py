"""Cocotb testbench for full adder."""
import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_full_adder_all_cases(dut):
    for a in range(2):
        for b in range(2):
            for cin in range(2):
                dut.a.value = a
                dut.b.value = b
                dut.cin.value = cin
                await Timer(2, units="ns")
                total = a + b + cin
                expected_sum = total & 1
                expected_cout = (total >> 1) & 1
                assert dut.sum.value == expected_sum, (
                    f"a={a} b={b} cin={cin}: sum expected {expected_sum} got {dut.sum.value}"
                )
                assert dut.cout.value == expected_cout, (
                    f"a={a} b={b} cin={cin}: cout expected {expected_cout} got {dut.cout.value}"
                )
