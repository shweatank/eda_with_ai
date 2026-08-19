import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_and_gate(dut):

    # Test 0 AND 0
    dut.a.value = 0
    dut.b.value = 0

    await Timer(1, units="ns")

    assert dut.u_and.y.value == 0

    print("PASS: 0 AND 0 = 0")


    # Test 0 AND 1
    dut.a.value = 0
    dut.b.value = 1

    await Timer(1, units="ns")

    assert dut.u_and.y.value == 0

    print("PASS: 0 AND 1 = 0")


    # Test 1 AND 0
    dut.a.value = 1
    dut.b.value = 0

    await Timer(1, units="ns")

    assert dut.u_and.y.value == 0

    print("PASS: 1 AND 0 = 0")


    # Test 1 AND 1
    dut.a.value = 1
    dut.b.value = 1

    await Timer(1, units="ns")

    assert dut.u_and.y.value == 1

    print("PASS: 1 AND 1 = 1")


@cocotb.test()
async def test_nand_gate(dut):

    # Test 0 NAND 0
    dut.a.value = 0
    dut.b.value = 0

    await Timer(1, units="ns")

    assert dut.u_nand.y.value == 1

    print("PASS: 0 NAND 0 = 1")


    # Test 0 NAND 1
    dut.a.value = 0
    dut.b.value = 1

    await Timer(1, units="ns")

    assert dut.u_nand.y.value == 1

    print("PASS: 0 NAND 1 = 1")


    # Test 1 NAND 0
    dut.a.value = 1
    dut.b.value = 0

    await Timer(1, units="ns")

    assert dut.u_nand.y.value == 1

    print("PASS: 1 NAND 0 = 1")


    # Test 1 NAND 1
    dut.a.value = 1
    dut.b.value = 1

    await Timer(1, units="ns")

    assert dut.u_nand.y.value == 0

    print("PASS: 1 NAND 1 = 0")

@cocotb.test()
async def test_nor_gate(dut):

    # Test 0 NOR 0
    dut.a.value = 0
    dut.b.value = 0

    await Timer(1, units="ns")

    assert dut.u_nor.y.value == 1

    print("PASS: 0 NOR 0 = 1")


    # Test 0 NOR 1
    dut.a.value = 0
    dut.b.value = 1

    await Timer(1, units="ns")

    assert dut.u_nor.y.value == 0

    print("PASS: 0 NOR 1 = 0")


    # Test 1 NOR 0
    dut.a.value = 1
    dut.b.value = 0

    await Timer(1, units="ns")

    assert dut.u_nor.y.value == 0

    print("PASS: 1 NOR 0 = 0")


    # Test 1 NOR 1
    dut.a.value = 1
    dut.b.value = 1

    await Timer(1, units="ns")

    assert dut.u_nor.y.value == 0

    print("PASS: 1 NOR 1 = 0")


@cocotb.test()
async def test_not_gate(dut):

    # Test 0 AND 0
    dut.a.value = 0

    await Timer(1, units="ns")

    assert dut.u_not.y.value == 1

    print("PASS: ~0 = 1")


    # Test 0 AND 1
    dut.a.value = 1

    await Timer(1, units="ns")

    assert dut.u_not.y.value == 0

    print("PASS: ~1 = 0")


@cocotb.test()
async def test_or_gate(dut):

    # Test 0 OR 0
    dut.a.value = 0
    dut.b.value = 0

    await Timer(1, units="ns")

    assert dut.u_or.y.value == 0

    print("PASS: 0 OR 0 = 0")


    # Test 0 OR 1
    dut.a.value = 0
    dut.b.value = 1

    await Timer(1, units="ns")

    assert dut.u_or.y.value == 1

    print("PASS: 0 OR 1 = 1")


    # Test 1 OR 0
    dut.a.value = 1
    dut.b.value = 0

    await Timer(1, units="ns")

    assert dut.u_or.y.value == 1

    print("PASS: 1 OR 0 = 1")


    # Test 1 OR 1
    dut.a.value = 1
    dut.b.value = 1

    await Timer(1, units="ns")

    assert dut.u_or.y.value == 1

    print("PASS: 1 OR 1 = 1")


@cocotb.test()
async def test_xor_gate(dut):

    # Test 0 XOR 0
    dut.a.value = 0
    dut.b.value = 0

    await Timer(1, units="ns")

    assert dut.u_xor.y.value == 0

    print("PASS: 0 XOR 0 = 0")


    # Test 0 XOR 1
    dut.a.value = 0
    dut.b.value = 1

    await Timer(1, units="ns")

    assert dut.u_xor.y.value == 1

    print("PASS: 0 XOR 1 = 1")


    # Test 1 XOR 0
    dut.a.value = 1
    dut.b.value = 0

    await Timer(1, units="ns")

    assert dut.u_xor.y.value == 1

    print("PASS: 1 XOR 0 = 1")


    # Test 1 XOR 1
    dut.a.value = 1
    dut.b.value = 1

    await Timer(1, units="ns")

    assert dut.u_xor.y.value == 0

    print("PASS: 1 XOR 1 = 0")