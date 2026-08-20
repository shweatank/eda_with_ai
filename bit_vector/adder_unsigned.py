import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def adder_unsigned(dut):
    # Test 1: Typical case, no overflow
    dut.a.value = 5
    dut.b.value = 10
    await Timer(1, units="ns")
    assert dut.sum.value == 15
    print("PASS: 5 + 10 = 15")

    # Test 2: Zero case
    dut.a.value = 0
    dut.b.value = 0
    await Timer(1, units="ns")
    assert dut.sum.value == 0
    print("PASS: 0 + 0 = 0")

    # Test 3: Max value + zero 
    dut.a.value = 255
    dut.b.value = 0
    await Timer(1, units="ns")
    assert dut.sum.value == 255
    print("PASS: 255 + 0 = 255")

    # Test 4: Just barely overflows 
    dut.a.value = 255
    dut.b.value = 1
    await Timer(1, units="ns")
    assert dut.sum.value == 0
    print("PASS: 255 + 1 = 0 (overflow)")

    # Test 5: Symmetric overflow case 
    dut.a.value = 128
    dut.b.value = 128
    await Timer(1, units="ns")
    assert dut.sum.value == 0
    print("PASS: 128 + 128 = 0 (overflow)")

    # Test 6: Maximum possible overflow 
    dut.a.value = 255
    dut.b.value = 255
    await Timer(1, units="ns")
    assert dut.sum.value == 254
    print("PASS: 255 + 255 = 254 (max overflow)")
