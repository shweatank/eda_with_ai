import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def mux2(dut):
    # Test 1: sel = 0 -> y = a (a=0, b=1)
    dut.a.value = 0
    dut.b.value = 1
    dut.sel.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: sel=0, a=0, b=1 -> y=0")

    # Test 2: sel = 0 -> y = a (a=1, b=0)
    dut.a.value = 1
    dut.b.value = 0
    dut.sel.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: sel=0, a=1, b=0 -> y=1")

    # Test 3: sel = 1 -> y = b (a=0, b=1)
    dut.a.value = 0
    dut.b.value = 1
    dut.sel.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: sel=1, a=0, b=1 -> y=1")

    # Test 4: sel = 1 -> y = b (a=1, b=0)
    dut.a.value = 1
    dut.b.value = 0
    dut.sel.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: sel=1, a=1, b=0 -> y=0")

    # Test 5: sel = 0, a=b=1 (edge case, both inputs same)
    dut.a.value = 1
    dut.b.value = 1
    dut.sel.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: sel=0, a=1, b=1 -> y=1")

    # Test 6: sel = 1, a=b=0 (edge case, both inputs same)
    dut.a.value = 0
    dut.b.value = 0
    dut.sel.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: sel=1, a=0, b=0 -> y=0")
