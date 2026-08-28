import cocotb
from cocotb.triggers import Timer
import os


@cocotb.test()
async def test_and_gate(dut):

    a = int(os.environ["INPUT_A"])
    b = int(os.environ["INPUT_B"])

    dut.a.value = a
    dut.b.value = b

    await Timer(1, unit="ns")

    y = int(dut.y.value)
    expected = a & b

    print(f"RESULT:{a},{b},{y}")

    assert y == expected