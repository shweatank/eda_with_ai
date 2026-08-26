import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ReadOnly, RisingEdge, Timer


async def sample_after_rising_edge(dut):
    """Wait until sequential logic has updated for this clock edge."""
    await RisingEdge(dut.clk)
    await ReadOnly()
    value = int(dut.y.value)
    # Leave the read-only simulator phase before driving the next vector.
    await Timer(1, unit="ps")
    return value


@cocotb.test()
async def test_and_ff(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.reset.value = 1
    dut.a.value = 0
    dut.b.value = 0
    assert await sample_after_rising_edge(dut) == 0
    print("PASS: Reset")

    dut.reset.value = 0

    for a, b, expected in ((0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 1)):
        dut.a.value = a
        dut.b.value = b
        assert await sample_after_rising_edge(dut) == expected
        print(f"PASS: {a} & {b} = {expected}")

    print("================================")
    print("AND + FF TEST PASSED")
    print("================================")
