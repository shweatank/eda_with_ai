import cocotb
from cocotb.triggers import Timer


async def check_and_gate(dut):
    dut.a.value = 0; dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: 0 AND 0 = 0")

    dut.a.value = 0; dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: 0 AND 1 = 0")

    dut.a.value = 1; dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: 1 AND 0 = 0")

    dut.a.value = 1; dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: 1 AND 1 = 1")


async def check_nand_gate(dut):
    dut.a.value = 0; dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: 0 NAND 0 = 1")

    dut.a.value = 0; dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: 0 NAND 1 = 1")

    dut.a.value = 1; dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: 1 NAND 0 = 1")

    dut.a.value = 1; dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: 1 NAND 1 = 0")


async def check_nor_gate(dut):
    dut.a.value = 0; dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: 0 NOR 0 = 1")

    dut.a.value = 0; dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: 0 NOR 1 = 0")

    dut.a.value = 1; dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: 1 NOR 0 = 0")

    dut.a.value = 1; dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: 1 NOR 1 = 0")


async def check_not_gate(dut):
    dut.a.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: NOT 0 = 1")

    dut.a.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: NOT 1 = 0")


async def check_or_gate(dut):
    dut.a.value = 0; dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: 0 OR 0 = 0")

    dut.a.value = 0; dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: 0 OR 1 = 1")

    dut.a.value = 1; dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: 1 OR 0 = 1")

    dut.a.value = 1; dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: 1 OR 1 = 1")


async def check_xor_gate(dut):
    dut.a.value = 0; dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: 0 XOR 0 = 0")

    dut.a.value = 0; dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: 0 XOR 1 = 1")

    dut.a.value = 1; dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.y.value == 1
    print("PASS: 1 XOR 0 = 1")

    dut.a.value = 1; dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == 0
    print("PASS: 1 XOR 1 = 0")


# Map DUT module name -> the coroutine that tests it
_GATE_TESTS = {
    "and_gate": check_and_gate,
    "nand_gate": check_nand_gate,
    "nor_gate": check_nor_gate,
    "not_gate": check_not_gate,
    "or_gate": check_or_gate,
    "xor_gate": check_xor_gate,
}


@cocotb.test()
async def test_gate(dut):
    """Single registered test that dispatches based on the loaded DUT module."""
    gate_name = dut._name
    test_func = _GATE_TESTS.get(gate_name)
    if test_func is None:
        raise ValueError(
            f"No test defined for DUT module '{gate_name}'. "
            f"Known gates: {list(_GATE_TESTS)}"
        )
    await test_func(dut)