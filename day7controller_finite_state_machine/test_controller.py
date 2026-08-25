import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

IDLE = 0b00
LOAD = 0b01
RUN = 0b10
DONE = 0b11


async def reset_dut(dut):
    dut.reset.value = 1
    dut.start.value = 0
    dut.finish.value = 0

    await Timer(20, units="ns")

    dut.reset.value = 0
    await RisingEdge(dut.clk)


@cocotb.test()
async def test_controller_fsm(dut):

    cocotb.start_soon(
        Clock(dut.clk, 10, units="ns").start()
    )

    dut.reset.value = 0
    dut.start.value = 0
    dut.finish.value = 0

    # TEST 1: RESET
    await reset_dut(dut)

    assert int(dut.busy.value) == 0
    assert int(dut.done.value) == 0
    assert int(dut.current_state.value) == IDLE

    dut._log.info("TEST 1 PASSED: Reset -> IDLE")

    # TEST 2: IDLE -> LOAD
    dut.start.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert int(dut.current_state.value) == LOAD
    assert int(dut.busy.value) == 1

    dut._log.info("TEST 2 PASSED: IDLE -> LOAD")

    dut.start.value = 0

    # TEST 3: LOAD -> RUN
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert int(dut.current_state.value) == RUN
    assert int(dut.busy.value) == 1

    dut._log.info("TEST 3 PASSED: LOAD -> RUN")

    # TEST 4: RUN -> RUN
    dut.finish.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert int(dut.current_state.value) == RUN
    assert int(dut.busy.value) == 1

    dut._log.info("TEST 4 PASSED: RUN -> RUN")

    # TEST 5: RUN -> DONE
    dut.finish.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert int(dut.current_state.value) == DONE
    assert int(dut.busy.value) == 0
    assert int(dut.done.value) == 1

    dut._log.info("TEST 5 PASSED: RUN -> DONE")

    dut.finish.value = 0

    # TEST 6: DONE -> IDLE
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert int(dut.current_state.value) == IDLE
    assert int(dut.busy.value) == 0
    assert int(dut.done.value) == 0

    dut._log.info("TEST 6 PASSED: DONE -> IDLE")

    # TEST 7: Second operation
    dut.start.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert int(dut.current_state.value) == LOAD

    dut._log.info("TEST 7 PASSED: Second operation started")

    dut.start.value = 0

    # TEST 8: Reset during operation
    dut.reset.value = 1

    await Timer(1, units="ns")

    assert int(dut.current_state.value) == IDLE
    assert int(dut.busy.value) == 0
    assert int(dut.done.value) == 0

    dut._log.info("TEST 8 PASSED: Reset during operation")

    dut.reset.value = 0

    dut._log.info("================================")
    dut._log.info("ALL TESTS PASSED")
    dut._log.info("================================")