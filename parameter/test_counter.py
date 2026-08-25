import cocotb

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


# ================================================================
# RESET FUNCTION
# ================================================================

async def reset_counter(dut):

    dut.reset.value = 1

    await Timer(2, units="ns")

    assert int(dut.count.value) == 0, (
        f"Reset failed: Expected count=0, "
        f"got {int(dut.count.value)}"
    )


# ================================================================
# RELEASE RESET
# ================================================================

async def release_reset(dut):

    dut.reset.value = 0

    await Timer(1, units="ns")


# ================================================================
# WAIT FOR CLOCK AND CHECK COUNT
# ================================================================

async def check_count(dut, expected):

    await RisingEdge(dut.clk)

    await Timer(1, units="ns")

    actual = int(dut.count.value)

    assert actual == expected, (
        f"COUNT TEST FAILED: "
        f"Expected {expected}, "
        f"got {actual}"
    )


# ================================================================
# MAIN TEST
# ================================================================

@cocotb.test()
async def test_counter(dut):


    # ============================================================
    # START CLOCK
    # ============================================================

    cocotb.start_soon(
        Clock(
            dut.clk,
            10,
            units="ns"
        ).start()
    )


    # ============================================================
    # INITIALIZATION
    # ============================================================

    dut.reset.value = 0

    await Timer(1, units="ns")


    dut._log.info("==========================================")
    dut._log.info("PARAMETERIZED COUNTER TEST STARTED")
    dut._log.info("==========================================")


    # ============================================================
    # TEST 1
    # INITIAL RESET
    # ============================================================

    await reset_counter(dut)

    dut._log.info(
        "TEST 1 PASSED: Counter reset = 0"
    )


    # ============================================================
    # TEST 2
    # RELEASE RESET
    # ============================================================

    await release_reset(dut)

    dut._log.info(
        "TEST 2 PASSED: Reset released"
    )


    # ============================================================
    # TEST 3
    # FIRST COUNT
    # ============================================================

    await check_count(
        dut,
        1
    )

    dut._log.info(
        "TEST 3 PASSED: Count = 1"
    )


    # ============================================================
    # TEST 4
    # SECOND COUNT
    # ============================================================

    await check_count(
        dut,
        2
    )

    dut._log.info(
        "TEST 4 PASSED: Count = 2"
    )


    # ============================================================
    # TEST 5
    # THIRD COUNT
    # ============================================================

    await check_count(
        dut,
        3
    )

    dut._log.info(
        "TEST 5 PASSED: Count = 3"
    )


    # ============================================================
    # TEST 6
    # MULTIPLE INCREMENTS
    # ============================================================

    for expected_count in range(4, 11):

        await check_count(
            dut,
            expected_count
        )


    dut._log.info(
        "TEST 6 PASSED: Counts 4 through 10"
    )


    # ============================================================
    # TEST 7
    # SECOND RESET
    # ============================================================

    dut.reset.value = 1

    await Timer(2, units="ns")

    assert int(dut.count.value) == 0, (
        f"TEST 7 FAILED: "
        f"Expected count=0 after second reset, "
        f"got {int(dut.count.value)}"
    )

    dut._log.info(
        "TEST 7 PASSED: Second reset"
    )


    # ============================================================
    # TEST 8
    # COUNT AFTER SECOND RESET
    # ============================================================

    dut.reset.value = 0

    await check_count(
        dut,
        1
    )

    dut._log.info(
        "TEST 8 PASSED: Count restarted from 1"
    )


    # ============================================================
    # TEST 9
    # ASYNCHRONOUS RESET
    #
    # Reset does NOT wait for clock.
    # ============================================================

    dut.reset.value = 1

    await Timer(1, units="ns")

    assert int(dut.count.value) == 0, (
        f"TEST 9 FAILED: "
        f"Asynchronous reset did not immediately clear count. "
        f"Got {int(dut.count.value)}"
    )

    dut._log.info(
        "TEST 9 PASSED: Asynchronous reset"
    )


    # ============================================================
    # TEST 10
    # RESET RELEASE
    # ============================================================

    dut.reset.value = 0

    await check_count(
        dut,
        1
    )

    dut._log.info(
        "TEST 10 PASSED: Counter resumed after reset"


    )


    # ============================================================
    # TEST 11
    # COUNT TO 255
    #
    # WIDTH = 8
    #
    # Maximum value = 255
    # ============================================================

    current_count = 1

    while current_count < 255:

        current_count += 1

        await check_count(
            dut,
            current_count
        )


    assert int(dut.count.value) == 255, (
        f"TEST 11 FAILED: "
        f"Expected count=255, "
        f"got {int(dut.count.value)}"
    )

    dut._log.info(
        "TEST 11 PASSED: Counter reached 255"
    )


    # ============================================================
    # TEST 12
    # OVERFLOW / WRAP AROUND
    #
    # 255 + 1 = 0 for an 8-bit counter
    # ============================================================

    await check_count(
        dut,
        0
    )

    dut._log.info(
        "TEST 12 PASSED: 255 → 0 overflow"
    )


    # ============================================================
    # TEST 13
    # VERIFY NEXT COUNTS AFTER OVERFLOW
    # ============================================================

    await check_count(
        dut,
        1
    )

    await check_count(
        dut,
        2
    )

    await check_count(
        dut,
        3
    )

    dut._log.info(
        "TEST 13 PASSED: Counting resumed after overflow"
    )


    # ============================================================
    # TEST 14
    # RESET DURING COUNTING
    # ============================================================

    dut.reset.value = 1

    await Timer(
        1,
        units="ns"
    )

    assert int(dut.count.value) == 0, (
        f"TEST 14 FAILED: "
        f"Reset during counting failed"
    )

    dut.reset.value = 0

    dut._log.info(
        "TEST 14 PASSED: Reset during counting"
    )


    # ============================================================
    # TEST 15
    # VERIFY COUNT RESTART
    # ============================================================

    await check_count(
        dut,
        1
    )

    await check_count(
        dut,
        2
    )

    await check_count(
        dut,
        3
    )

    dut._log.info(
        "TEST 15 PASSED: Counter restart verified"
    )


    # ============================================================
    # COMPLETE
    # ============================================================

    dut._log.info("")
    dut._log.info("==========================================")
    dut._log.info("ALL COUNTER TESTS PASSED")
    dut._log.info("15 TEST GROUPS PASSED")
    dut._log.info("==========================================")