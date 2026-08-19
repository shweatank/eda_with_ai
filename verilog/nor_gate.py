import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_nor_gate(dut):
    # Test 0 NOR 0
    dut.a.value = 0
    dut.b.value = 0
    await Timer(1, units="ns")
    assert dut.y.value == 1
    print("PASS: 0 NOR 0 = 1")

    # Test 0 NOR 1
    dut.a.value = 0
    dut.b.value = 1
    await Timer(1, units="ns")
    assert dut.y.value == 0
    print("PASS: 0 NOR 1 = 0")

    # Test 1 NOR 0
    dut.a.value = 1
    dut.b.value = 0
    await Timer(1, units="ns")
    assert dut.y.value == 0
    print("PASS: 1 NOR 0 = 0")

    # Test 1 NOR 1
    dut.a.value = 1
    dut.b.value = 1
    await Timer(1, units="ns")
    assert dut.y.value == 0
    print("PASS: 1 NOR 1 = 0")
