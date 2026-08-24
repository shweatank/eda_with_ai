import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_mux(dut):

    # S = 0 → output should be A
    dut.A.value = 0
    dut.B.value = 1
    dut.S.value = 0

    await Timer(1, units="ns")

    assert dut.Y.value == 0
    print("Test 1 passed")


    # S = 0 → output should be A
    dut.A.value = 1
    dut.B.value = 0
    dut.S.value = 0

    await Timer(1, units="ns")

    assert dut.Y.value == 1
    print("Test 2 passed")


    # S = 1 → output should be B
    dut.A.value = 0
    dut.B.value = 1
    dut.S.value = 1

    await Timer(1, units="ns")

    assert dut.Y.value == 1
    print("Test 3 passed")


    # S = 1 → output should be B
    dut.A.value = 1
    dut.B.value = 0
    dut.S.value = 1

    await Timer(1, units="ns")

    assert dut.Y.value == 0
    print("Test 4 passed")