import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_subtractor(dut):
    # Test 1: Typical case, no borrow
    dut.a.value = 10
    dut.b.value = 5
    await Timer(1, units="ns")
    assert dut.diff.value == 5
    print("PASS: 10 - 5 = 5")

    # Test 2: Equal values
    dut.a.value = 7
    dut.b.value = 7
    await Timer(1, units="ns")
    assert dut.diff.value == 0
    print("PASS: 7 - 7 = 0")

    # Test 3: Zero minus zero 
    dut.a.value = 0
    dut.b.value = 0
    await Timer(1, units="ns")
    assert dut.diff.value == 0
    print("PASS: 0 - 0 = 0")

    # Test 4: Max value minus zero 
    dut.a.value = 255
    dut.b.value = 0
    await Timer(1, units="ns")
    assert dut.diff.value == 255
    print("PASS: 255 - 0 = 255")

    # Test 5: Borrow case (a < b), just barely
    dut.a.value = 0
    dut.b.value = 1
    await Timer(1, units="ns")
    assert dut.diff.value == 255  
    print("PASS: 0 - 1 = 255 (borrow/underflow)")

    # Test 6: Max possible borrow 
    dut.a.value = 0
    dut.b.value = 255
    await Timer(1, units="ns")
    assert dut.diff.value == 1 
    print("PASS: 0 - 255 = 1 (max borrow/underflow)")
