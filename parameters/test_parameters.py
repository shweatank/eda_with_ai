import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def test_counter(dut):

    # Start clock: 10 ns period
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # -----------------------------
    # Apply reset
    # -----------------------------
    dut.reset.value = 1

    await Timer(20, units="ns")

    # Counter should be 0 after reset
    assert dut.count.value == 0, \
        f"Expected count=0 after reset, got {dut.count.value}"

    # Release reset
    dut.reset.value = 0

    # -----------------------------
    # Check counter increment
    # -----------------------------
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert dut.count.value == 1, \
        f"Expected count=1, got {dut.count.value}"

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert dut.count.value == 2, \
        f"Expected count=2, got {dut.count.value}"

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert dut.count.value == 3, \
        f"Expected count=3, got {dut.count.value}"

    # -----------------------------
    # Check several increments
    # -----------------------------
    for expected_count in range(4, 11):

        await RisingEdge(dut.clk)
        await Timer(1, units="ns")

        assert dut.count.value == expected_count, \
            f"Expected {expected_count}, got {dut.count.value}"

    # -----------------------------
    # Apply reset again
    # -----------------------------
    dut.reset.value = 1

    await Timer(2, units="ns")

    assert dut.count.value == 0, \
        f"Expected count=0 after second reset, got {dut.count.value}"

    dut.reset.value = 0

    print("Counter test PASSED")