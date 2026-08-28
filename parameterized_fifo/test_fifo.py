import cocotb
import os
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


async def clock_cycle(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")


async def write_word(dut, value):
    dut.write_data.value = value
    dut.write_enable.value = 1
    dut.read_enable.value = 0
    await clock_cycle(dut)
    dut.write_enable.value = 0


async def read_word(dut):
    dut.read_enable.value = 1
    dut.write_enable.value = 0
    await clock_cycle(dut)
    dut.read_enable.value = 0
    return int(dut.read_data.value)


@cocotb.test()
async def test_parameterized_fifo(dut):
    data_width = len(dut.write_data)
    depth = int(os.environ.get("FIFO_DEPTH", "8"))
    data_mask = (1 << data_width) - 1
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.reset.value = 1
    dut.write_enable.value = 0
    dut.read_enable.value = 0
    dut.write_data.value = 0
    await Timer(12, unit="ns")
    dut.reset.value = 0
    await clock_cycle(dut)

    assert int(dut.empty.value) == 1
    assert int(dut.full.value) == 0
    assert int(dut.count.value) == 0

    expected = [(index * 0x1357 + 0x2A) & data_mask for index in range(depth)]
    for value in expected:
        await write_word(dut, value)

    assert int(dut.full.value) == 1
    assert int(dut.empty.value) == 0
    assert int(dut.count.value) == depth

    dut.write_data.value = 0xDEAD & data_mask
    dut.write_enable.value = 1
    await clock_cycle(dut)
    dut.write_enable.value = 0
    assert int(dut.overflow.value) == 1
    assert int(dut.count.value) == depth

    for index, expected_value in enumerate(expected):
        actual_value = await read_word(dut)
        print(f"READ {index}: expected=0x{expected_value:X} actual=0x{actual_value:X}")
        assert actual_value == expected_value

    assert int(dut.empty.value) == 1
    dut.read_enable.value = 1
    await clock_cycle(dut)
    dut.read_enable.value = 0
    assert int(dut.underflow.value) == 1

    print(f"PARAMETERIZED FIFO PASSED: DATA_WIDTH={data_width}, FIFO_DEPTH={depth}")
