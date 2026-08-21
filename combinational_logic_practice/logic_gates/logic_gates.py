import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def logic_gates(dut):
    # Test 1: a=0, b=0
    dut.a.value = 0
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.and_out.value == 0
    assert dut.or_out.value == 0
    assert dut.nand_out.value == 1
    assert dut.nor_out.value == 1
    print("PASS: a=0, b=0 -> AND=0, OR=0, NAND=1, NOR=1")

    # Test 2: a=0, b=1
    dut.a.value = 0
    dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.and_out.value == 0
    assert dut.or_out.value == 1
    assert dut.nand_out.value == 1
    assert dut.nor_out.value == 0
    print("PASS: a=0, b=1 -> AND=0, OR=1, NAND=1, NOR=0")

    # Test 3: a=1, b=0
    dut.a.value = 1
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.and_out.value == 0
    assert dut.or_out.value == 1
    assert dut.nand_out.value == 1
    assert dut.nor_out.value == 0
    print("PASS: a=1, b=0 -> AND=0, OR=1, NAND=1, NOR=0")

    # Test 4: a=1, b=1
    dut.a.value = 1
    dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.and_out.value == 1
    assert dut.or_out.value == 1
    assert dut.nand_out.value == 0
    assert dut.nor_out.value == 0
    print("PASS: a=1, b=1 -> AND=1, OR=1, NAND=0, NOR=0")
