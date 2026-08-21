import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_alu(dut):

    dut.a.value = 10
    dut.b.value = 5

    # ADD
    dut.op.value = 0
    await Timer(1, units="ns")

    print("ADD =", int(dut.result.value))

    # SUB
    dut.op.value = 1
    await Timer(1, units="ns")

    print("SUB =", int(dut.result.value))

    # MUL
    dut.op.value = 2
    await Timer(1, units="ns")

    print("MUL =", int(dut.result.value))

    # DIV
    dut.op.value = 3
    await Timer(1, units="ns")

    print("DIV =", int(dut.result.value))
    
    
    dut.a.value = 4
    dut.b.value = 2

    # ADD
    dut.op.value = 0
    await Timer(1, units="ns")

    print("ADD =", int(dut.result.value))

    # SUB
    dut.op.value = 1
    await Timer(1, units="ns")

    print("SUB =", int(dut.result.value))

    # MUL
    dut.op.value = 2
    await Timer(1, units="ns")

    print("MUL =", int(dut.result.value))

    # DIV
    dut.op.value = 3
    await Timer(1, units="ns")

    print("DIV =", int(dut.result.value))
