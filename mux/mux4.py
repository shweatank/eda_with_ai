import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def mux4(dut):
    # Test 1: sel = 00 -> y = d[0]
    dut.d.value = 0b0001
    dut.sel.value = 0b00
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: sel=00, d=0001 -> y=1 (d[0])")

    # Test 2: sel = 01 -> y = d[1]
    dut.d.value = 0b0010
    dut.sel.value = 0b01
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: sel=01, d=0010 -> y=1 (d[1])")

    # Test 3: sel = 10 -> y = d[2]
    dut.d.value = 0b0100
    dut.sel.value = 0b10
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: sel=10, d=0100 -> y=1 (d[2])")

    # Test 4: sel = 11 -> y = d[3]
    dut.d.value = 0b1000
    dut.sel.value = 0b11
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: sel=11, d=1000 -> y=1 (d[3])")

    # Test 5: sel = 00, but d[0] = 0 -> y should be 0 
    dut.d.value = 0b1110
    dut.sel.value = 0b00
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: sel=00, d=1110 -> y=0 (d[0]=0)")

    # Test 6: sel = 01, d[1] = 0 -> y = 0
    dut.d.value = 0b1101
    dut.sel.value = 0b01
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: sel=01, d=1101 -> y=0 (d[1]=0)")

    # Test 7: sel = 10, d[2] = 0 -> y = 0
    dut.d.value = 0b1011
    dut.sel.value = 0b10
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: sel=10, d=1011 -> y=0 (d[2]=0)")

    # Test 8: sel = 11, d[3] = 0 -> y = 0
    dut.d.value = 0b0111
    dut.sel.value = 0b11
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: sel=11, d=0111 -> y=0 (d[3]=0)")

    # Test 9: All d bits high, cycle through every sel value
    dut.d.value = 0b1111
    for sel_val in range(4):
        dut.sel.value = sel_val
        await Timer(1, unit="ns")
        assert dut.y.value == 1
        print(f"PASS: sel={sel_val:02b}, d=1111 -> y=1")

    # Test 10: All d bits low, cycle through every sel value
    dut.d.value = 0b0000
    for sel_val in range(4):
        dut.sel.value = sel_val
        await Timer(1, unit="ns")
        assert dut.y.value == 0
        print(f"PASS: sel={sel_val:02b}, d=0000 -> y=0")
