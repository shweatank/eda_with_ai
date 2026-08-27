import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_vector_and(dut):

    # Test 1
    dut.a.value = 0b10101010
    dut.b.value = 0b11001100

    await Timer(1, unit="ns")

    expected = 0b10001000

    assert int(dut.y.value) == expected, \
        f"Expected {expected:08b}, got {int(dut.y.value):08b}"

    dut._log.info("TEST 1 PASSED")

    # Test 2
    dut.a.value = 0xFF
    dut.b.value = 0x0F

    await Timer(1, unit="ns")

    expected = 0x0F

    assert int(dut.y.value) == expected, \
        f"Expected 0x{expected:02X}, got 0x{int(dut.y.value):02X}"

    dut._log.info("TEST 2 PASSED")

    # Test 3
    dut.a.value = 0x00
    dut.b.value = 0xFF

    await Timer(1, unit="ns")

    assert int(dut.y.value) == 0x00

    dut._log.info("TEST 3 PASSED")

    # Test 4
    dut.a.value = 0xFF
    dut.b.value = 0xFF

    await Timer(1, unit="ns")

    assert int(dut.y.value) == 0xFF

    dut._log.info("TEST 4 PASSED")

    dut._log.info("==============================")
    dut._log.info("ALL VECTOR AND TESTS PASSED")
    dut._log.info("==============================")