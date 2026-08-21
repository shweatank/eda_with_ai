import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def half_adder(dut):
    # Test 1: 0 + 0 = 0, carry 0
    dut.a.value = 0
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.sum.value == 0
    assert dut.carry.value == 0
    print("PASS: 0 + 0 -> sum=0, carry=0")

    # Test 2: 0 + 1 = 1, carry 0
    dut.a.value = 0
    dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.sum.value == 1
    assert dut.carry.value == 0
    print("PASS: 0 + 1 -> sum=1, carry=0")

    # Test 3: 1 + 0 = 1, carry 0
    dut.a.value = 1
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.sum.value == 1
    assert dut.carry.value == 0
    print("PASS: 1 + 0 -> sum=1, carry=0")

    # Test 4: 1 + 1 = 0, carry 1
    dut.a.value = 1
    dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.sum.value == 0
    assert dut.carry.value == 1
    print("PASS: 1 + 1 -> sum=0, carry=1")
