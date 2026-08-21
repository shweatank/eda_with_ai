import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_multiplier(dut):
    # Test 1: Typical case
    dut.a.value = 5
    dut.b.value = 6
    await Timer(1, units="ns")
    assert dut.product.value == 30
    print("PASS: 5 * 6 = 30")

    # Test 2: Multiply by zero
    dut.a.value = 200
    dut.b.value = 0
    await Timer(1, units="ns")
    assert dut.product.value == 0
    print("PASS: 200 * 0 = 0")

    # Test 3: Multiply by one 
    dut.a.value = 123
    dut.b.value = 1
    await Timer(1, units="ns")
    assert dut.product.value == 123
    print("PASS: 123 * 1 = 123")

    # Test 4: Both small values
    dut.a.value = 3
    dut.b.value = 4
    await Timer(1, units="ns")
    assert dut.product.value == 12
    print("PASS: 3 * 4 = 12")

    # Test 5: Max value squared 
    dut.a.value = 255
    dut.b.value = 255
    await Timer(1, units="ns")
    assert dut.product.value == 65025
    print("PASS: 255 * 255 = 65025")

    # Test 6: One max value, one mid-range value
    dut.a.value = 255
    dut.b.value = 100
    await Timer(1, units="ns")
    assert dut.product.value == 25500
    print("PASS: 255 * 100 = 25500")
