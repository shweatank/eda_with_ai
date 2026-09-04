import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_xor_gate(dut):

    # Test 0 XOR 0 → 0
    dut.a.value = 0
    dut.b.value = 0
    await Timer(1, units="ns")
    assert dut.y.value == 0
    print("PASS: 0 XOR 0 = 0")

    # Test 0 XOR 1 → 1
    dut.a.value = 0
    dut.b.value = 1
    await Timer(1, units="ns")
    assert dut.y.value == 1
    print("PASS: 0 XOR 1 = 1")

    # Test 1 XOR 0 → 1
    dut.a.value = 1
    dut.b.value = 0
    await Timer(1, units="ns")
    assert dut.y.value == 1
    print("PASS: 1 XOR 0 = 1")

    # Test 1 XOR 1 → 0
    dut.a.value = 1
    dut.b.value = 1
    await Timer(1, units="ns")
    assert dut.y.value == 0
    print("PASS: 1 XOR 1 = 0")
