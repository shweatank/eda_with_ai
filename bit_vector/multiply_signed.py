import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_multiplier(dut):
    # Test 1: Typical positive case
    dut.a.value = 5
    dut.b.value = 6
    await Timer(1, units="ns")
    assert dut.product.value.signed_integer == 30
    print("PASS: 5 * 6 = 30")

    # Test 2: Multiply by zero
    dut.a.value = -50
    dut.b.value = 0
    await Timer(1, units="ns")
    assert dut.product.value.signed_integer == 0
    print("PASS: -50 * 0 = 0")

    # Test 3: Positive * negative
    dut.a.value = 10
    dut.b.value = -5
    await Timer(1, units="ns")
    assert dut.product.value.signed_integer == -50
    print("PASS: 10 * (-5) = -50")

    # Test 4: Negative * negative 
    dut.a.value = -4
    dut.b.value = -3
    await Timer(1, units="ns")
    assert dut.product.value.signed_integer == 12
    print("PASS: (-4) * (-3) = 12")

    # Test 5: Multiply by one 
    dut.a.value = -77
    dut.b.value = 1
    await Timer(1, units="ns")
    assert dut.product.value.signed_integer == -77
    print("PASS: -77 * 1 = -77")

    # Test 6: Max positive * max positive
    dut.a.value = 127
    dut.b.value = 127
    await Timer(1, units="ns")
    assert dut.product.value.signed_integer == 16129
    print("PASS: 127 * 127 = 16129")

    # Test 7: Min negative * min negative 
    dut.a.value = -128
    dut.b.value = -128
    await Timer(1, units="ns")
    assert dut.product.value.signed_integer == 16384
    print("PASS: (-128) * (-128) = 16384")

    # Test 8: Min negative * max positive
    dut.a.value = -128
    dut.b.value = 127
    await Timer(1, units="ns")
    assert dut.product.value.signed_integer == -16256
    print("PASS: (-128) * 127 = -16256")
