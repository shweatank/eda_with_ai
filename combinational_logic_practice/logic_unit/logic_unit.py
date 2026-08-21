import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def logic_unit(dut):
    # ---------------- sel = 00 -> AND ----------------
    dut.sel.value = 0b00
    dut.a.value = 0
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: sel=00 (AND), a=0, b=0 -> y=0")

    dut.a.value = 1
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: sel=00 (AND), a=1, b=0 -> y=0")

    dut.a.value = 1
    dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: sel=00 (AND), a=1, b=1 -> y=1")

    # ---------------- sel = 01 -> OR ----------------
    dut.sel.value = 0b01
    dut.a.value = 0
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: sel=01 (OR), a=0, b=0 -> y=0")

    dut.a.value = 1
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: sel=01 (OR), a=1, b=0 -> y=1")

    dut.a.value = 0
    dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: sel=01 (OR), a=0, b=1 -> y=1")

    # ---------------- sel = 10 -> NAND ----------------
    dut.sel.value = 0b10
    dut.a.value = 1
    dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: sel=10 (NAND), a=1, b=1 -> y=0")

    dut.a.value = 0
    dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: sel=10 (NAND), a=0, b=1 -> y=1")

    dut.a.value = 0
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: sel=10 (NAND), a=0, b=0 -> y=1")

    # ---------------- sel = 11 -> NOR ----------------
    dut.sel.value = 0b11
    dut.a.value = 0
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: sel=11 (NOR), a=0, b=0 -> y=1")

    dut.a.value = 1
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: sel=11 (NOR), a=1, b=0 -> y=0")

    dut.a.value = 1
    dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: sel=11 (NOR), a=1, b=1 -> y=0")

    
