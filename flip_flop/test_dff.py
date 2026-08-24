import cocotb

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def test_dff_1bit(dut):

    dut._log.info("======================================")
    dut._log.info("Starting D Flip-Flop verification")
    dut._log.info("======================================")

    # 10 ns clock
    cocotb.start_soon(
        Clock(dut.clk, 10, units="ns").start()
    )

    # ------------------------------------------------------------
    # Test 1: asynchronous reset
    # ------------------------------------------------------------

    dut.reset.value = 1
    dut.d.value = 0

    await Timer(2, units="ns")

    assert dut.q.value.integer == 0, (
        f"Reset failed: expected q=0, got q={dut.q.value}"
    )

    dut._log.info("PASS: asynchronous reset")

    # ------------------------------------------------------------
    # Test 2: capture 1
    # ------------------------------------------------------------

    dut.reset.value = 0
    dut.d.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert dut.q.value.integer == 1, (
        f"Capture 1 failed: expected q=1, got q={dut.q.value}"
    )

    dut._log.info("PASS: D=1 captured")

    # ------------------------------------------------------------
    # Test 3: capture 0
    # ------------------------------------------------------------

    dut.d.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert dut.q.value.integer == 0, (
        f"Capture 0 failed: expected q=0, got q={dut.q.value}"
    )

    dut._log.info("PASS: D=0 captured")

    # ------------------------------------------------------------
    # Test 4: D changes without clock
    # ------------------------------------------------------------

    dut.d.value = 1

    await Timer(3, units="ns")

    assert dut.q.value.integer == 0, (
        "DFF changed without clock edge"
    )

    dut._log.info(
        "PASS: q remains stable without rising edge"
    )

    # ------------------------------------------------------------
    # Test 5: asynchronous reset while running
    # ------------------------------------------------------------

    dut.reset.value = 1

    await Timer(1, units="ns")

    assert dut.q.value.integer == 0, (
        f"Async reset failed: q={dut.q.value}"
    )

    dut._log.info(
        "PASS: asynchronous reset during operation"
    )

    dut.reset.value = 0

    dut._log.info("======================================")
    dut._log.info("DFF TEST PASSED")
    dut._log.info("======================================")
