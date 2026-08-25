import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_vector_and(dut):

    # Test 1: All zeros
    dut.a.value = 0x00
    dut.b.value = 0x00
    await Timer(1, units="ns")

    assert dut.y.value == 0x00
    print("Test 1 PASS: 00 & 00 = 00")


    # Test 2: All ones
    dut.a.value = 0xFF
    dut.b.value = 0xFF
    await Timer(1, units="ns")

    assert dut.y.value == 0xFF
    print("Test 2 PASS: FF & FF = FF")


    # Test 3: One input zero
    dut.a.value = 0x00
    dut.b.value = 0xFF
    await Timer(1, units="ns")

    assert dut.y.value == 0x00
    print("Test 3 PASS: 00 & FF = 00")


    # Test 4: Partial overlap
    dut.a.value = 0xAA
    dut.b.value = 0x55
    await Timer(1, units="ns")

    assert dut.y.value == 0x00
    print("Test 4 PASS: AA & 55 = 00")


    # Test 5: Partial bits
    dut.a.value = 0xF0
    dut.b.value = 0x0F
    await Timer(1, units="ns")

    assert dut.y.value == 0x00
    print("Test 5 PASS: F0 & 0F = 00")


    # Test 6: Same pattern
    dut.a.value = 0xA5
    dut.b.value = 0xA5
    await Timer(1, units="ns")

    assert dut.y.value == 0xA5
    print("Test 6 PASS: A5 & A5 = A5")


    # Test 7: Random-looking values
    dut.a.value = 0x3C
    dut.b.value = 0x0F
    await Timer(1, units="ns")

    assert dut.y.value == 0x0C
    print("Test 7 PASS: 3C & 0F = 0C")


    print("===================================")
    print("     VECTOR AND TEST PASSED        ")
    print("===================================")
