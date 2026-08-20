import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def adder_signed(dut):
    # Test 1: Typical positive case
    dut.a.value = 5
    dut.b.value = 10
    await Timer(1, units="ns")
    assert dut.sum.value.signed_integer == 15
    print("PASS: 5 + 10 = 15")

    # Test 2: Zero case
    dut.a.value = 0
    dut.b.value = 0
    await Timer(1, units="ns")
    assert dut.sum.value.signed_integer == 0
    print("PASS: 0 + 0 = 0")

    # Test 3: Max positive boundary, no overflow
    dut.a.value = 127
    dut.b.value = 0
    await Timer(1, units="ns")
    assert dut.sum.value.signed_integer == 127
    print("PASS: 127 + 0 = 127")

    # Test 4: Positive overflow 
    dut.a.value = 127
    dut.b.value = 1
    await Timer(1, units="ns")
    assert dut.sum.value.signed_integer == -128
    print("PASS: 127 + 1 = -128 (positive overflow)")

    # Test 5: Negative number, typical case
    dut.a.value = -5
    dut.b.value = 10
    await Timer(1, units="ns")
    assert dut.sum.value.signed_integer == 5
    print("PASS: -5 + 10 = 5")

    # Test 6: Two negative numbers
    dut.a.value = -20
    dut.b.value = -30
    await Timer(1, units="ns")
    assert dut.sum.value.signed_integer == -50
    print("PASS: -20 + (-30) = -50")

    # Test 7: Min negative boundary, no underflow
    dut.a.value = -128
    dut.b.value = 0
    await Timer(1, units="ns")
    assert dut.sum.value.signed_integer == -128
    print("PASS: -128 + 0 = -128")

    # Test 8: Negative overflow / underflow 
    dut.a.value = -100
    dut.b.value = -100
    await Timer(1, units="ns")
    assert dut.sum.value.signed_integer == 56
    print("PASS: -100 + (-100) = 56 (negative overflow)")
