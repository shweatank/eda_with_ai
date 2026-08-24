import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def test_dff_1bit(dut):
    """Verify reset, storage and data capture."""

    # Start a 10 ns clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Set initial inputs
    dut.reset.value = 1
    dut.d.value = 0

    await Timer(2, units="ns")

    # Asynchronous reset must clear q immediately
    assert dut.q.value == 0, (
        f"Reset failed: expected q=0, received q={dut.q.value}"
    )

    cocotb.log.info("PASS: Reset cleared q")

    # Release reset
    dut.reset.value = 0

    # Test storing 1
    dut.d.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert dut.q.value == 1, (
        f"Store-1 failed: expected q=1, received q={dut.q.value}"
    )

    cocotb.log.info("PASS: DFF stored 1")

    # Change d between clock edges
    dut.d.value = 0
    await Timer(2, units="ns")

    # q must retain its previous value until the next edge
    assert dut.q.value == 1, (
        f"Storage failed: q changed before clock edge to {dut.q.value}"
    )

    cocotb.log.info("PASS: DFF retained previous value")

    # Capture 0 on the next rising edge
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert dut.q.value == 0, (
        f"Store-0 failed: expected q=0, received q={dut.q.value}"
    )

    cocotb.log.info("PASS: DFF stored 0")

    # Test asynchronous reset while q contains 1
    dut.d.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert dut.q.value == 1

    # Assert reset without waiting for a clock edge
    dut.reset.value = 1
    await Timer(1, units="ns")

    assert dut.q.value == 0, (
        f"Asynchronous reset failed: q={dut.q.value}"
    )

    cocotb.log.info("PASS: Asynchronous reset worked")
    cocotb.log.info("ALL D FLIP-FLOP TESTS PASSED")