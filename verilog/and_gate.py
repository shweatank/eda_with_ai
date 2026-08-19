import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_and_gate(dut):

    # Test 0 AND 0
    dut.a.value = 0
    dut.b.value = 0

    await Timer(1, units="ns")

    assert dut.y.value == 0

    print("PASS: 0 AND 0 = 0")


    # Test 0 AND 1
    dut.a.value = 0
    dut.b.value = 1

    await Timer(1, units="ns")

    assert dut.y.value == 0

    print("PASS: 0 AND 1 = 0")


    # Test 1 AND 0
    dut.a.value = 1
    dut.b.value = 0

    await Timer(1, units="ns")

    assert dut.y.value == 0

    print("PASS: 1 AND 0 = 0")


    # Test 1 AND 1
    dut.a.value = 1
    dut.b.value = 1

    await Timer(1, units="ns")

    assert dut.y.value == 1

    print("PASS: 1 AND 1 = 1")
