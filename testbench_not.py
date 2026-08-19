import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_not_gate(dut):

    # Test NOT 0 → 1
    dut.a.value = 0
    await Timer(1, units="ns")
    assert dut.y.value == 1
    print("PASS: NOT 0 = 1")

    # Test NOT 1 → 0
    dut.a.value = 1
    await Timer(1, units="ns")
    assert dut.y.value == 0
    print("PASS: NOT 1 = 0")
