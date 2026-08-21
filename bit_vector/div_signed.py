import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def div_signed(dut):
    # Test 1: Typical positive case
    dut.a.value = 20
    dut.b.value = 4
    await Timer(1, unit="ns")
    assert dut.quotient.value.signed_integer == 5
    assert dut.remainder.value.signed_integer == 0
    print("PASS: 20 / 4 = 5 remainder 0")

    # Test 2: Positive dividend, negative divisor
    dut.a.value = 20
    dut.b.value = -4
    await Timer(1, unit="ns")
    assert dut.quotient.value.signed_integer == -5
    assert dut.remainder.value.signed_integer == 0
    print("PASS: 20 / -4 = -5 remainder 0")

    # Test 3: Negative dividend, positive divisor 
    dut.a.value = -7
    dut.b.value = 2
    await Timer(1, unit="ns")
    assert dut.quotient.value.signed_integer == -3  
    assert dut.remainder.value.signed_integer == -1  
    print("PASS: -7 / 2 = -3 remainder -1")

    # Test 4: Both negative 
    dut.a.value = -20
    dut.b.value = -4
    await Timer(1, unit="ns")
    assert dut.quotient.value.signed_integer == 5
    assert dut.remainder.value.signed_integer == 0
    print("PASS: -20 / -4 = 5 remainder 0")

    # Test 5: Dividend smaller than divisor 
    dut.a.value = 3
    dut.b.value = -10
    await Timer(1, unit="ns")
    assert dut.quotient.value.signed_integer == 0
    assert dut.remainder.value.signed_integer == 3
    print("PASS: 3 / -10 = 0 remainder 3")

    # Test 6: Zero dividend
    dut.a.value = 0
    dut.b.value = -7
    await Timer(1, unit="ns")
    assert dut.quotient.value.signed_integer == 0
    assert dut.remainder.value.signed_integer == 0
    print("PASS: 0 / -7 = 0 remainder 0")

    # Test 7: Divide by one 
    dut.a.value = -100
    dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.quotient.value.signed_integer == -100
    assert dut.remainder.value.signed_integer == 0
    print("PASS: -100 / 1 = -100 remainder 0")

    # Test 8: Divide by -1 
    dut.a.value = -127
    dut.b.value = -1
    await Timer(1, unit="ns")
    assert dut.quotient.value.signed_integer == 127
    assert dut.remainder.value.signed_integer == 0
    print("PASS: -127 / -1 = 127 remainder 0")

    # Test 9: Division by zero 
    dut.a.value = 10
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert str(dut.quotient.value).upper() == "XXXXXXXX"
    assert str(dut.remainder.value).upper() == "XXXXXXXX"
    print("PASS: 10 / 0 -> quotient and remainder are undefined (X), as expected")
