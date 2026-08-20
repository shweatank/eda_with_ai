import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_four_bit_adder(dut):

    # Give input values
    a = 10
    b = 5
    cin = 0

    # Apply inputs to DUT
    dut.a.value = a
    dut.b.value = b
    dut.cin.value = cin

    # Wait for combinational logic
    await Timer(1, units="ns")

    # Read outputs
    sum_value = int(dut.sum.value)
    cout_value = int(dut.cout.value)

   
