import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def div_unsigned(dut):
    # Test 1: Typical case, exact division
    dut.a.value = 20
    dut.b.value = 4
    await Timer(1, unit="ns")
    assert dut.quotient.value == 5
    assert dut.remainder.value == 0
    print("PASS: 20 / 4 = 5 remainder 0")

    # Test 2: Division with a remainder
    dut.a.value = 17
    dut.b.value = 5
    await Timer(1, unit="ns")
    assert dut.quotient.value == 3
    assert dut.remainder.value == 2
    print("PASS: 17 / 5 = 3 remainder 2")

    # Test 3: Dividend smaller than divisor 
    dut.a.value = 3
    dut.b.value = 10
    await Timer(1, unit="ns")
    assert dut.quotient.value == 0
    assert dut.remainder.value == 3
    print("PASS: 3 / 10 = 0 remainder 3")

    # Test 4: Zero dividend
    dut.a.value = 0
    dut.b.value = 7
    await Timer(1, unit="ns")
    assert dut.quotient.value == 0
    assert dut.remainder.value == 0
    print("PASS: 0 / 7 = 0 remainder 0")

    # Test 5: Divide by one 
    dut.a.value = 200
    dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.quotient.value == 200
    assert dut.remainder.value == 0
    print("PASS: 200 / 1 = 200 remainder 0")

    # Test 6: Max value divided by itself
    dut.a.value = 255
    dut.b.value = 255
    await Timer(1, unit="ns")
    assert dut.quotient.value == 1
    assert dut.remainder.value == 0
    print("PASS: 255 / 255 = 1 remainder 0")

    # Test 7: Division by zero 
    dut.a.value = 10
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert str(dut.quotient.value).upper() == "XXXXXXXX"
    assert str(dut.remainder.value).upper() == "XXXXXXXX"
    print("PASS: 10 / 0 -> quotient and remainder are undefined (X), as expected")
