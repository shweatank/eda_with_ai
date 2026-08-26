import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def dff_1bit(dut):
    # Step 1: Initialize all inputs to known values first
    dut.clk.value = 0
    dut.d.value = 0
    await Timer(1, unit="ns")

    # Step 2: Start the clock only after initial state has settled
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Step 3: Let a throwaway clock edge pass, then a tiny settle delay,
    # to guarantee q's non-blocking update has fully propagated
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    # Test 1: d=0 held, q should now be 0
    assert dut.q.value == 0
    print("PASS: d=0 -> q=0 (after clock edge)")

    # Test 2: d=1, q should capture it on the next clock edge
    dut.d.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    assert dut.q.value == 1
    print("PASS: d=1 -> q=1 (after clock edge)")

    # Test 3: d changes back to 0
    dut.d.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    assert dut.q.value == 0
    print("PASS: d=0 -> q=0 (after clock edge)")

    # Test 4: d toggles across consecutive edges
    dut.d.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    assert dut.q.value == 1
    print("PASS: d=1 -> q=1")

    dut.d.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    assert dut.q.value == 0
    print("PASS: d=0 -> q=0")

    # Test 5: Confirm q does NOT change if d changes but no clock edge has occurred yet
    dut.d.value = 1
    await Timer(1, unit="ns")   # small delay, but NOT a clock edge
    assert dut.q.value == 0     # q should still be the old value (0)
    print("PASS: d changed mid-cycle, q unchanged until next clock edge")

    # Now let the pending clock edge happen, q should finally update
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    assert dut.q.value == 1
    print("PASS: q updates to 1 only after the actual clock edge")
