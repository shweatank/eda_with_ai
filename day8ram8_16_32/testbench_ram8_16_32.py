"""Cocotb testbench for ram8_16_32.

The RTL is parameterized on DATA_WIDTH (8/16/32/...) and ADDR_WIDTH
(sets DEPTH = 2**ADDR_WIDTH). Rather than hardcoding a width, this
testbench reads DATA_WIDTH / ADDR_WIDTH from the environment -- the
Makefile exports them and also passes them to the simulator as
compile-time parameter overrides (-P...), so the Python side and the
compiled RTL always agree on the same width.

Covers:
  - basic write-then-read-back across several addresses
  - write-first same-cycle forwarding (write+read same address on the
    same clock edge returns the NEW data)
  - a full (or sampled, for large depths) sweep of every address
  - randomized read/write stress test against a Python shadow memory
"""

import os
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

DATA_WIDTH = int(os.environ.get("DATA_WIDTH", "8"))
ADDR_WIDTH = int(os.environ.get("ADDR_WIDTH", "8"))
DEPTH = 1 << ADDR_WIDTH
DATA_MASK = (1 << DATA_WIDTH) - 1
ADDR_MASK = DEPTH - 1

HEX_DIGITS = (DATA_WIDTH + 3) // 4


def hx(v):
    return f"0x{v & DATA_MASK:0{HEX_DIGITS}X}"


async def start_clock(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())


async def reset_inputs(dut):
    dut.we.value = 0
    dut.addr.value = 0
    dut.din.value = 0
    await RisingEdge(dut.clk)


async def ram_write(dut, addr, data):
    dut.we.value = 1
    dut.addr.value = addr
    dut.din.value = data
    await RisingEdge(dut.clk)
    dut.we.value = 0


async def ram_read(dut, addr):
    dut.we.value = 0
    dut.addr.value = addr
    await RisingEdge(dut.clk)
    # Let the nonblocking dout <= ... assignment from this edge settle.
    await Timer(1, unit="ns")
    return int(dut.dout.value)


@cocotb.test()
async def test_write_then_read_back(dut):
    """Write distinct values to a handful of addresses, then read every
    one back afterwards and confirm the RAM actually held each value."""
    await start_clock(dut)
    await reset_inputs(dut)

    dut._log.info(
        f"DATA_WIDTH={DATA_WIDTH} ADDR_WIDTH={ADDR_WIDTH} DEPTH={DEPTH}"
    )

    sample_addrs = sorted(
        {0, ADDR_MASK, DEPTH // 2 & ADDR_MASK, min(3, ADDR_MASK), min(11, ADDR_MASK)}
    )
    expected = {}

    for addr in sample_addrs:
        data = random.randint(0, DATA_MASK)
        expected[addr] = data
        await ram_write(dut, addr, data)
        dut._log.info(f"WRITE addr=0x{addr:X} data={hx(data)}")

    for addr in sample_addrs:
        actual = await ram_read(dut, addr)
        assert actual == expected[addr], (
            f"addr=0x{addr:X}: expected {hx(expected[addr])}, got {hx(actual)}"
        )
        dut._log.info(f"READ  addr=0x{addr:X} data={hx(actual)} OK")

    dut._log.info("test_write_then_read_back PASSED")


@cocotb.test()
async def test_write_first_same_cycle_forwarding(dut):
    """Writing and reading the SAME address on the SAME clock edge must
    return the value being written this cycle (write-first), not the
    stale value that was there before."""
    await start_clock(dut)
    await reset_inputs(dut)

    addr = min(5, ADDR_MASK)
    old_val = random.randint(0, DATA_MASK)
    new_val = random.randint(0, DATA_MASK)
    while new_val == old_val:
        new_val = random.randint(0, DATA_MASK)

    # Seed the location with a known old value first.
    await ram_write(dut, addr, old_val)
    readback = await ram_read(dut, addr)
    assert readback == old_val, (
        f"seed write failed: expected {hx(old_val)}, got {hx(readback)}"
    )

    # Now write new_val to the same address; dout should forward new_val
    # on this very edge, not old_val.
    dut.we.value = 1
    dut.addr.value = addr
    dut.din.value = new_val
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.we.value = 0

    forwarded = int(dut.dout.value)
    assert forwarded == new_val, (
        f"write-first forwarding failed: expected {hx(new_val)}, "
        f"got {hx(forwarded)}"
    )
    dut._log.info(
        f"addr=0x{addr:X}: old={hx(old_val)} -> new={hx(new_val)} "
        f"forwarded={hx(forwarded)} OK"
    )

    # And the write actually landed in memory too.
    confirm = await ram_read(dut, addr)
    assert confirm == new_val, (
        f"post-write read expected {hx(new_val)}, got {hx(confirm)}"
    )

    dut._log.info("test_write_first_same_cycle_forwarding PASSED")


@cocotb.test()
async def test_address_sweep(dut):
    """Write a unique pattern to every address (or a bounded sample for
    very deep memories) and confirm every location reads back correctly,
    proving addresses don't alias each other."""
    await start_clock(dut)
    await reset_inputs(dut)

    # Full sweep for small memories, evenly-spaced sample for large ones
    # so simulation time stays reasonable.
    MAX_SWEEP = 256
    if DEPTH <= MAX_SWEEP:
        addrs = list(range(DEPTH))
    else:
        step = DEPTH // MAX_SWEEP
        addrs = list(range(0, DEPTH, step))[:MAX_SWEEP]

    expected = {}
    for addr in addrs:
        pattern = (addr * 2654435761 + 0xA5) & DATA_MASK  # Knuth-ish scramble
        expected[addr] = pattern
        await ram_write(dut, addr, pattern)

    for addr in addrs:
        actual = await ram_read(dut, addr)
        assert actual == expected[addr], (
            f"addr=0x{addr:X}: expected {hx(expected[addr])}, got {hx(actual)}"
        )

    dut._log.info(
        f"test_address_sweep PASSED ({len(addrs)} of {DEPTH} addresses checked)"
    )


@cocotb.test()
async def test_random_stress(dut):
    """Randomized read/write stress test checked against a Python shadow
    memory -- the closest thing to a real access pattern."""
    await start_clock(dut)
    await reset_inputs(dut)

    shadow = {}
    ITERATIONS = 300

    for _ in range(ITERATIONS):
        addr = random.randint(0, ADDR_MASK)
        do_write = (not shadow) or random.random() < 0.6

        if do_write:
            data = random.randint(0, DATA_MASK)
            await ram_write(dut, addr, data)
            shadow[addr] = data
        else:
            # Only check addresses we know the value of.
            known_addrs = [a for a in shadow if a == addr] or list(shadow.keys())
            addr = random.choice(known_addrs)
            actual = await ram_read(dut, addr)
            assert actual == shadow[addr], (
                f"stress addr=0x{addr:X}: expected {hx(shadow[addr])}, "
                f"got {hx(actual)}"
            )

    # Final full check of every address we ever wrote.
    for addr, data in shadow.items():
        actual = await ram_read(dut, addr)
        assert actual == data, (
            f"final check addr=0x{addr:X}: expected {hx(data)}, got {hx(actual)}"
        )

    dut._log.info(
        f"test_random_stress PASSED ({ITERATIONS} ops, "
        f"{len(shadow)} unique addresses touched)"
    )