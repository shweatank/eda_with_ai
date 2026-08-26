import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

# FSM state encoding
IDLE = 0b00
LOAD = 0b01
RUN  = 0b10
DONE = 0b11


async def reset_dut(dut):
    """Apply reset to DUT."""
    dut.reset.value = 1
    dut.start.value = 0
    dut.finish.value = 0

    await Timer(20, unit="ns")

    dut.reset.value = 0

    await RisingEdge(dut.clk)


@cocotb.test()
async def test_fsm(dut):

    # Start clock
    cocotb.start_soon(
        Clock(dut.clk, 10, unit="ns").start()
    )

    # Initial values
    dut.reset.value = 0
    dut.start.value = 0
    dut.finish.value = 0

    # --------------------------------------------------
    # TEST 1: RESET
    # --------------------------------------------------
    await reset_dut(dut)

    assert dut.busy.value == 0, \
        "FAIL: busy should be 0 after reset"
    assert dut.done.value == 0, \
        "FAIL: done should be 0 after reset"
    assert dut.current_state.value == IDLE, \
        "FAIL: FSM should be in IDLE after reset"

    dut._log.info("TEST 1 PASSED: Reset -> IDLE")

    # --------------------------------------------------
    # TEST 2: IDLE -> LOAD
    # --------------------------------------------------
    dut.start.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert dut.current_state.value == LOAD, \
        "FAIL: IDLE -> LOAD transition"
    assert dut.busy.value == 1, \
        "FAIL: busy should be 1 in LOAD"

    dut._log.info("TEST 2 PASSED: IDLE -> LOAD")

    dut.start.value = 0

    # --------------------------------------------------
    # TEST 3: LOAD -> RUN
    # --------------------------------------------------
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert dut.current_state.value == RUN, \
        "FAIL: LOAD -> RUN transition"
    assert dut.busy.value == 1, \
        "FAIL: busy should be 1 in RUN"

    dut._log.info("TEST 3 PASSED: LOAD -> RUN")

    # --------------------------------------------------
    # TEST 4: RUN remains RUN
    # --------------------------------------------------
    dut.finish.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert dut.current_state.value == RUN, \
        "FAIL: FSM should remain in RUN"
    assert dut.busy.value == 1, \
        "FAIL: busy should remain 1 in RUN"

    dut._log.info("TEST 4 PASSED: RUN -> RUN")

    # --------------------------------------------------
    # TEST 5: RUN -> DONE
    # --------------------------------------------------
    dut.finish.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert dut.current_state.value == DONE, \
        "FAIL: RUN -> DONE transition"
    assert dut.busy.value == 0, \
        "FAIL: busy should be 0 in DONE"
    assert dut.done.value == 1, \
        "FAIL: done should be 1 in DONE"

    dut._log.info("TEST 5 PASSED: RUN -> DONE")

    dut.finish.value = 0

    # --------------------------------------------------
    # TEST 6: DONE -> IDLE
    # --------------------------------------------------
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert dut.current_state.value == IDLE, \
        "FAIL: DONE -> IDLE transition"
    assert dut.busy.value == 0, \
        "FAIL: busy should be 0 in IDLE"
    assert dut.done.value == 0, \
        "FAIL: done should be 0 in IDLE"

    dut._log.info("TEST 6 PASSED: DONE -> IDLE")

    # --------------------------------------------------
    # TEST 7: Start second operation
    # --------------------------------------------------
    dut.start.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert dut.current_state.value == LOAD, \
        "FAIL: Second operation did not enter LOAD"

    dut._log.info("TEST 7 PASSED: Second operation started")

    dut.start.value = 0

    # --------------------------------------------------
    # TEST 8: Reset during operation
    # --------------------------------------------------
    dut.reset.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert dut.current_state.value == IDLE, \
        "FAIL: Reset should force FSM to IDLE"
    assert dut.busy.value == 0, \
        "FAIL: busy should be 0 after reset"
    assert dut.done.value == 0, \
        "FAIL: done should be 0 after reset"

    dut._log.info("TEST 8 PASSED: Reset during operation")

    dut.reset.value = 0

    # --------------------------------------------------
    # COMPLETE
    # --------------------------------------------------
    dut._log.info("====================================")
    dut._log.info("ALL TESTS PASSED")
    dut._log.info("====================================")
