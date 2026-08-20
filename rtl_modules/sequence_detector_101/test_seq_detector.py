"""Cocotb testbench for the '101' overlapping sequence detector."""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


async def reset(dut):
    dut.rst_n.value = 0
    dut.din.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    dut.rst_n.value = 1


@cocotb.test()
async def test_seq_detector_basic(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    await reset(dut)

    # Reference model: Moore FSM matching in this file's design
    stream = "1101011011101"  # contains overlapping "101" patterns
    state = 0  # 0=S0,1=S1,2=S2,3=S3
    expected_bits = []

    for bit in stream:
        b = int(bit)
        if state == 0:
            state = 1 if b else 0
        elif state == 1:
            state = 1 if b else 2
        elif state == 2:
            state = 3 if b else 0
        elif state == 3:
            state = 1 if b else 2
        expected_bits.append(1 if state == 3 else 0)

    for bit, expected in zip(stream, expected_bits):
        dut.din.value = int(bit)
        await RisingEdge(dut.clk)
        await Timer(1, units="ns")
        assert dut.detected.value == expected, (
            f"bit={bit}: expected detected={expected}, got {dut.detected.value}"
        )
