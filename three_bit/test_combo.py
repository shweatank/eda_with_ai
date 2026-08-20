import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_or_gate(dut):

    # 1.Test 0 AND 0 OR 0
    dut.a.value = 0
    dut.b.value = 0
    dut.c.value = 0

    await Timer(1, unit="ns")

    assert dut.y.value == 0

    print("PASS: 0 AND 0 OR 0 = 0")


    # 2.Test 0 AND 0 OR 1
    dut.a.value = 0
    dut.b.value = 0
    dut.c.value = 1

    await Timer(1, unit="ns")

    assert dut.y.value == 1

    print("PASS: 0 AND 0 OR 1 = 1")

    # 3.Test 0 AND 1 OR 0
    dut.a.value = 0
    dut.b.value = 1
    dut.c.value = 0

    await Timer(1, unit="ns")
    assert dut.y.value == 0 
    print("PASS: 0 AND 1 OR 0 = 0")

    # 4.Test 0 AND 1 OR 1
    dut.a.value = 0
    dut.b.value = 1
    dut.c.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: 0 AND 1 OR 1 = 1")

    # 5.Test 1 AND 0 OR 0
    dut.a.value = 1
    dut.b.value = 0
    dut.c.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: 1 AND 0 OR 0 = 0")

    # 6.Test 1 AND 0 OR 1
    dut.a.value = 1
    dut.b.value = 0
    dut.c.value = 1 
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: 1 AND 0 OR 1 = 1")

    # 7.Test 1 AND 1 OR 0
    dut.a.value = 1
    dut.b.value = 1
    dut.c.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: 1 AND 1 OR 0 = 1")     

    # 8.Test 1 AND 1 OR 1
    dut.a.value = 1
    dut.b.value = 1 
    dut.c.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: 1 AND 1 OR 1 = 1")     

