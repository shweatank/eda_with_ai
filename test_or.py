import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_or_gate_basic(dut):

    # Test 1: a=0, b=0
    # Expected: y=0
    dut.a.value = 0
    dut.b.value = 0

    await Timer(2, units="ns")

    assert dut.y.value == 0, (
        f"OR gate failed for a=0, b=0: got y={dut.y.value}"
    )

    # Test 2: a=0, b=1
    # Expected: y=1
    dut.a.value = 0
    dut.b.value = 1

    await Timer(2, units="ns")

    assert dut.y.value == 1, (
        f"OR gate failed for a=0, b=1: got y={dut.y.value}"
    )

    # Test 3: a=1, b=0
    # Expected: y=1
    dut.a.value = 1
    dut.b.value = 0

    await Timer(2, units="ns")

    assert dut.y.value == 1, (
        f"OR gate failed for a=1, b=0: got y={dut.y.value}"
    )

    # Test 4: a=1, b=1
    # Expected: y=1
    dut.a.value = 1
    dut.b.value = 1

    await Timer(2, units="ns")

    assert dut.y.value == 1, (
        f"OR gate failed for a=1, b=1: got y={dut.y.value}"
    )