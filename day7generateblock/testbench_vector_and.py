import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_vector_and(dut):

    # -----------------------------------
    # Test 1
    # -----------------------------------
    dut.a.value = 0xFF
    dut.b.value = 0x0F

    await Timer(1, unit="ns")

    result = int(dut.y.value)

    assert result == 0x0F, \
        f"TEST 1 FAILED: Expected 0x0F, got 0x{result:02X}"

    dut._log.info("TEST 1 PASSED: FF & 0F = 0F")

    # -----------------------------------
    # Test 2
    # -----------------------------------
    dut.a.value = 0xAA
    dut.b.value = 0x55

    await Timer(1, unit="ns")

    result = int(dut.y.value)

    assert result == 0x00, \
        f"TEST 2 FAILED: Expected 0x00, got 0x{result:02X}"

    dut._log.info("TEST 2 PASSED: AA & 55 = 00")

    # -----------------------------------
    # Test 3
    # -----------------------------------
    dut.a.value = 0xF0
    dut.b.value = 0xCC

    await Timer(1, unit="ns")

    result = int(dut.y.value)

    assert result == 0xC0, \
        f"TEST 3 FAILED: Expected 0xC0, got 0x{result:02X}"

    dut._log.info("TEST 3 PASSED: F0 & CC = C0")

    # -----------------------------------
    # Test 4
    # -----------------------------------
    dut.a.value = 0x00
    dut.b.value = 0xFF

    await Timer(1, unit="ns")

    result = int(dut.y.value)

    assert result == 0x00, \
        f"TEST 4 FAILED: Expected 0x00, got 0x{result:02X}"

    dut._log.info("TEST 4 PASSED: 00 & FF = 00")

    # -----------------------------------
    # Test 5
    # -----------------------------------
    dut.a.value = 0xFF
    dut.b.value = 0xFF

    await Timer(1, unit="ns")

    result = int(dut.y.value)

    assert result == 0xFF, \
        f"TEST 5 FAILED: Expected 0xFF, got 0x{result:02X}"

    dut._log.info("TEST 5 PASSED: FF & FF = FF")

    dut._log.info("==============================")
    dut._log.info("ALL VECTOR AND TESTS PASSED")
    dut._log.info("==============================")