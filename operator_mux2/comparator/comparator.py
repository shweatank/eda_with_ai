import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def comparator(dut):
    # Test 1: a == b 
    dut.a.value = 50
    dut.b.value = 50
    await Timer(1, unit="ns")
    assert dut.equal.value == 1
    assert dut.greater.value == 0
    assert dut.less.value == 0
    print("PASS: 50 == 50 -> equal=1, greater=0, less=0")

    # Test 2: a > b
    dut.a.value = 100
    dut.b.value = 50
    await Timer(1, unit="ns")
    assert dut.equal.value == 0
    assert dut.greater.value == 1
    assert dut.less.value == 0
    print("PASS: 100 > 50 -> equal=0, greater=1, less=0")

    # Test 3: a < b
    dut.a.value = 50
    dut.b.value = 100
    await Timer(1, unit="ns")
    assert dut.equal.value == 0
    assert dut.greater.value == 0
    assert dut.less.value == 1
    print("PASS: 50 < 100 -> equal=0, greater=0, less=1")

    # Test 4: both zero 
    dut.a.value = 0
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.equal.value == 1
    assert dut.greater.value == 0
    assert dut.less.value == 0
    print("PASS: 0 == 0 -> equal=1, greater=0, less=0")

    # Test 5: both max value 
    dut.a.value = 255
    dut.b.value = 255
    await Timer(1, unit="ns")
    assert dut.equal.value == 1
    assert dut.greater.value == 0
    assert dut.less.value == 0
    print("PASS: 255 == 255 -> equal=1, greater=0, less=0")

    # Test 6: max vs zero 
    dut.a.value = 255
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.equal.value == 0
    assert dut.greater.value == 1
    assert dut.less.value == 0
    print("PASS: 255 > 0 -> equal=0, greater=1, less=0")

    # Test 7: zero vs max 
    dut.a.value = 0
    dut.b.value = 255
    await Timer(1, unit="ns")
    assert dut.equal.value == 0
    assert dut.greater.value == 0
    assert dut.less.value == 1
    print("PASS: 0 < 255 -> equal=0, greater=0, less=1")

    # Test 8: adjacent values 
    dut.a.value = 101
    dut.b.value = 100
    await Timer(1, unit="ns")
    assert dut.equal.value == 0
    assert dut.greater.value == 1
    assert dut.less.value == 0
    print("PASS: 101 > 100 -> equal=0, greater=1, less=0")
