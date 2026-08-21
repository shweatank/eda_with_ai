import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def decoder_2to4(dut):
    # Test 1: a = 00 -> y[0] active
    dut.a.value = 0b00
    await Timer(1, unit="ns")
    assert dut.y.value == 0b0001
    print("PASS: a=00 -> y=0001")

    # Test 2: a = 01 -> y[1] active
    dut.a.value = 0b01
    await Timer(1, unit="ns")
    assert dut.y.value == 0b0010
    print("PASS: a=01 -> y=0010")

    # Test 3: a = 10 -> y[2] active
    dut.a.value = 0b10
    await Timer(1, unit="ns")
    assert dut.y.value == 0b0100
    print("PASS: a=10 -> y=0100")

    # Test 4: a = 11 -> y[3] active
    dut.a.value = 0b11
    await Timer(1, unit="ns")
    assert dut.y.value == 0b1000
    print("PASS: a=11 -> y=1000")
