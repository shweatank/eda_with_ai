import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def sub_signed(dut):
    # Test 1: Typical positive case
    dut.a.value = 10
    dut.b.value = 5
    await Timer(1, units="ns")
    assert dut.diff.value.signed_integer == 5
    print("PASS: 10 - 5 = 5")

    # Test 2: Equal values
    dut.a.value = 7
    dut.b.value = 7
    await Timer(1, units="ns")
    assert dut.diff.value.signed_integer == 0
    print("PASS: 7 - 7 = 0")

    # Test 3: Result goes negative 
    dut.a.value = 5
    dut.b.value = 10
    await Timer(1, units="ns")
    assert dut.diff.value.signed_integer == -5
    print("PASS: 5 - 10 = -5")

    # Test 4: Negative input minus positive input
    dut.a.value = -50
    dut.b.value = 30
    await Timer(1, units="ns")
    assert dut.diff.value.signed_integer == -80
    print("PASS: -50 - 30 = -80")

    # Test 5: Two negative numbers
    dut.a.value = -20
    dut.b.value = -30
    await Timer(1, units="ns")
    assert dut.diff.value.signed_integer == 10
    print("PASS: -20 - (-30) = 10")

    # Test 6: Max positive boundary, no overflow
    dut.a.value = 127
    dut.b.value = 0
    await Timer(1, units="ns")
    assert dut.diff.value.signed_integer == 127
    print("PASS: 127 - 0 = 127")

    # Test 7: Positive overflow 
    dut.a.value = 127
    dut.b.value = -1
    await Timer(1, units="ns")
    assert dut.diff.value.signed_integer == -128
    print("PASS: 127 - (-1) = -128 (positive overflow)")

    # Test 8: Negative underflow 
    dut.a.value = -100
    dut.b.value = 50
    await Timer(1, units="ns")
    assert dut.diff.value.signed_integer == 106
    print("PASS: -100 - 50 = 106 (negative underflow)")
