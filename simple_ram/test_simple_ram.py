import cocotb

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


# ================================================================
# RESET / INITIALIZATION
# ================================================================

async def reset_ram(dut):

    dut.write_enable.value = 0
    dut.address.value = 0
    dut.write_data.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")


# ================================================================
# WRITE FUNCTION
# ================================================================

async def write_ram(dut, address, data):

    dut.write_enable.value = 1
    dut.address.value = address
    dut.write_data.value = data

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    dut.write_enable.value = 0


# ================================================================
# READ FUNCTION
# ================================================================

async def read_ram(dut, address):

    dut.write_enable.value = 0
    dut.address.value = address

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    return int(dut.read_data.value)


# ================================================================
# TEST
# ================================================================

@cocotb.test()
async def test_16bit_ram(dut):

    # ============================================================
    # START CLOCK
    # ============================================================

    cocotb.start_soon(
        Clock(dut.clk, 10, units="ns").start()
    )

    # ============================================================
    # INITIALIZATION
    # ============================================================

    dut.write_enable.value = 0
    dut.address.value = 0
    dut.write_data.value = 0

    await reset_ram(dut)

    dut._log.info("==========================================")
    dut._log.info("16-BIT RAM TEST STARTED")
    dut._log.info("==========================================")


    # ============================================================
    # TEST 1
    # ADDRESS 0x0000
    # DATA 0x0000
    # ============================================================

    await write_ram(
        dut,
        address=0x0000,
        data=0x0000
    )

    data = await read_ram(
        dut,
        address=0x0000
    )

    assert data == 0x0000, (
        f"TEST 1 FAILED: Expected 0x0000, got 0x{data:04X}"
    )

    dut._log.info(
        "TEST 1 PASSED: Address 0x0000 = 0x0000"
    )


    # ============================================================
    # TEST 2
    # ALL ONES
    # ============================================================

    await write_ram(
        dut,
        address=0x0001,
        data=0xFFFF
    )

    data = await read_ram(
        dut,
        address=0x0001
    )

    assert data == 0xFFFF, (
        f"TEST 2 FAILED: Expected 0xFFFF, got 0x{data:04X}"
    )

    dut._log.info(
        "TEST 2 PASSED: Address 0x0001 = 0xFFFF"
    )


    # ============================================================
    # TEST 3
    # ALTERNATING 1010
    # ============================================================

    await write_ram(
        dut,
        address=0x0010,
        data=0xAAAA
    )

    data = await read_ram(
        dut,
        address=0x0010
    )

    assert data == 0xAAAA, (
        f"TEST 3 FAILED: Expected 0xAAAA, got 0x{data:04X}"
    )

    dut._log.info(
        "TEST 3 PASSED: Address 0x0010 = 0xAAAA"
    )


    # ============================================================
    # TEST 4
    # ALTERNATING 0101
    # ============================================================

    await write_ram(
        dut,
        address=0x0020,
        data=0x5555
    )

    data = await read_ram(
        dut,
        address=0x0020
    )

    assert data == 0x5555, (
        f"TEST 4 FAILED: Expected 0x5555, got 0x{data:04X}"
    )

    dut._log.info(
        "TEST 4 PASSED: Address 0x0020 = 0x5555"
    )


    # ============================================================
    # TEST 5
    # RANDOM-STYLE PATTERN
    # ============================================================

    await write_ram(
        dut,
        address=0x0100,
        data=0x1234
    )

    data = await read_ram(
        dut,
        address=0x0100
    )

    assert data == 0x1234, (
        f"TEST 5 FAILED: Expected 0x1234, got 0x{data:04X}"
    )

    dut._log.info(
        "TEST 5 PASSED: Address 0x0100 = 0x1234"
    )


    # ============================================================
    # TEST 6
    # ANOTHER PATTERN
    # ============================================================

    await write_ram(
        dut,
        address=0x1000,
        data=0x5678
    )

    data = await read_ram(
        dut,
        address=0x1000
    )

    assert data == 0x5678, (
        f"TEST 6 FAILED: Expected 0x5678, got 0x{data:04X}"
    )

    dut._log.info(
        "TEST 6 PASSED: Address 0x1000 = 0x5678"
    )


    # ============================================================
    # TEST 7
    # HIGH BIT TEST
    # ============================================================

    await write_ram(
        dut,
        address=0x7FFF,
        data=0x8001
    )

    data = await read_ram(
        dut,
        address=0x7FFF
    )

    assert data == 0x8001, (
        f"TEST 7 FAILED: Expected 0x8001, got 0x{data:04X}"
    )

    dut._log.info(
        "TEST 7 PASSED: Address 0x7FFF = 0x8001"
    )


    # ============================================================
    # TEST 8
    # ADDRESS 0x8000
    # ============================================================

    await write_ram(
        dut,
        address=0x8000,
        data=0x8000
    )

    data = await read_ram(
        dut,
        address=0x8000
    )

    assert data == 0x8000, (
        f"TEST 8 FAILED: Expected 0x8000, got 0x{data:04X}"
    )

    dut._log.info(
        "TEST 8 PASSED: Address 0x8000 = 0x8000"
    )


    # ============================================================
    # TEST 9
    # NEAR MAXIMUM ADDRESS
    # ============================================================

    await write_ram(
        dut,
        address=0xFFFE,
        data=0xDEAD
    )

    data = await read_ram(
        dut,
        address=0xFFFE
    )

    assert data == 0xDEAD, (
        f"TEST 9 FAILED: Expected 0xDEAD, got 0x{data:04X}"
    )

    dut._log.info(
        "TEST 9 PASSED: Address 0xFFFE = 0xDEAD"
    )


    # ============================================================
    # TEST 10
    # MAXIMUM ADDRESS
    # ============================================================

    await write_ram(
        dut,
        address=0xFFFF,
        data=0xBEEF
    )

    data = await read_ram(
        dut,
        address=0xFFFF
    )

    assert data == 0xBEEF, (
        f"TEST 10 FAILED: Expected 0xBEEF, got 0x{data:04X}"
    )

    dut._log.info(
        "TEST 10 PASSED: Address 0xFFFF = 0xBEEF"
    )


    # ============================================================
    # TEST 11
    # CHECK DATA PERSISTENCE
    # ============================================================

    data = await read_ram(
        dut,
        address=0x0010
    )

    assert data == 0xAAAA, (
        f"TEST 11 FAILED: Address 0x0010 changed. "
        f"Expected 0xAAAA, got 0x{data:04X}"
    )

    data = await read_ram(
        dut,
        address=0x0020
    )

    assert data == 0x5555, (
        f"TEST 11 FAILED: Address 0x0020 changed. "
        f"Expected 0x5555, got 0x{data:04X}"
    )

    dut._log.info(
        "TEST 11 PASSED: Previous data remained intact"
    )


    # ============================================================
    # TEST 12
    # OVERWRITE ADDRESS 0x0010
    # ============================================================

    await write_ram(
        dut,
        address=0x0010,
        data=0x55AA
    )

    data = await read_ram(
        dut,
        address=0x0010
    )

    assert data == 0x55AA, (
        f"TEST 12 FAILED: Expected 0x55AA, got 0x{data:04X}"
    )

    dut._log.info(
        "TEST 12 PASSED: Address 0x0010 overwritten"
    )


    # ============================================================
    # TEST 13
    # WALKING BIT PATTERN
    # ============================================================

    walking_patterns = [
        0x0001,
        0x0002,
        0x0004,
        0x0008,
        0x0010,
        0x0020,
        0x0040,
        0x0080,
        0x0100,
        0x0200,
        0x0400,
        0x0800,
        0x1000,
        0x2000,
        0x4000,
        0x8000
    ]

    address = 0x0200

    for pattern in walking_patterns:

        await write_ram(
            dut,
            address=address,
            data=pattern
        )

        data = await read_ram(
            dut,
            address=address
        )

        assert data == pattern, (
            f"TEST 13 FAILED: "
            f"Expected 0x{pattern:04X}, "
            f"got 0x{data:04X}"
        )

    dut._log.info(
        "TEST 13 PASSED: Walking bit pattern"
    )


    # ============================================================
    # TEST 14
    # COMPLEMENT WALKING PATTERN
    # ============================================================

    complement_patterns = [
        0xFFFE,
        0xFFFD,
        0xFFFB,
        0xFFF7,
        0xFFEF,
        0xFFDF,
        0xFFBF,
        0xFF7F,
        0xFEFF,
        0xFDFF,
        0xFBFF,
        0xF7FF,
        0xEFFF,
        0xDFFF,
        0xBFFF,
        0x7FFF
    ]

    address = 0x0300

    for pattern in complement_patterns:

        await write_ram(
            dut,
            address=address,
            data=pattern
        )

        data = await read_ram(
            dut,
            address=address
        )

        assert data == pattern, (
            f"TEST 14 FAILED: "
            f"Expected 0x{pattern:04X}, "
            f"got 0x{data:04X}"
        )

    dut._log.info(
        "TEST 14 PASSED: Complement walking pattern"
    )


    # ============================================================
    # TEST 15
    # MULTIPLE ADDRESS TEST
    # ============================================================

    test_memory = {
        0x0100: 0x1111,
        0x0200: 0x2222,
        0x0300: 0x3333,
        0x0400: 0x4444,
        0x0500: 0x5555,
        0x0600: 0x6666,
        0x0700: 0x7777,
        0x0800: 0x8888,
        0x0900: 0x9999,
        0x0A00: 0xAAAA,
        0x0B00: 0xBBBB,
        0x0C00: 0xCCCC,
        0x0D00: 0xDDDD,
        0x0E00: 0xEEEE,
        0x0F00: 0xFFFF
    }

    for address, expected in test_memory.items():

        await write_ram(
            dut,
            address=address,
            data=expected
        )

    for address, expected in test_memory.items():

        data = await read_ram(
            dut,
            address=address
        )

        assert data == expected, (
            f"TEST 15 FAILED: "
            f"Address 0x{address:04X}: "
            f"Expected 0x{expected:04X}, "
            f"got 0x{data:04X}"
        )

    dut._log.info(
        "TEST 15 PASSED: Multiple address test"
    )


    # ============================================================
    # TEST 16
    # NEIGHBOR ADDRESS ISOLATION
    # ============================================================

    await write_ram(
        dut,
        address=0x1000,
        data=0xAAAA
    )

    await write_ram(
        dut,
        address=0x1001,
        data=0xBBBB
    )

    await write_ram(
        dut,
        address=0x1002,
        data=0xCCCC
    )

    data0 = await read_ram(dut, 0x1000)
    data1 = await read_ram(dut, 0x1001)
    data2 = await read_ram(dut, 0x1002)

    assert data0 == 0xAAAA, (
        f"TEST 16 FAILED: Address 0x1000 changed"
    )

    assert data1 == 0xBBBB, (
        f"TEST 16 FAILED: Address 0x1001 changed"
    )

    assert data2 == 0xCCCC, (
        f"TEST 16 FAILED: Address 0x1002 changed"
    )

    dut._log.info(
        "TEST 16 PASSED: Neighbor address isolation"
    )


    # ============================================================
    # TEST 17
    # ALL ZERO / ALL ONE
    # ============================================================

    await write_ram(
        dut,
        address=0x2000,
        data=0x0000
    )

    data = await read_ram(
        dut,
        address=0x2000
    )

    assert data == 0x0000

    await write_ram(
        dut,
        address=0x2000,
        data=0xFFFF
    )

    data = await read_ram(
        dut,
        address=0x2000
    )

    assert data == 0xFFFF

    dut._log.info(
        "TEST 17 PASSED: 0x0000 and 0xFFFF boundary data"
    )


    # ============================================================
    # TEST 18
    # DATA PATTERN TEST
    # ============================================================

    patterns = [
        0x0000,
        0xFFFF,
        0xAAAA,
        0x5555,
        0x1234,
        0x4321,
        0xDEAD,
        0xBEEF,
        0xCAFE,
        0xFACE,
        0x1357,
        0x2468
    ]

    address = 0x3000

    for pattern in patterns:

        await write_ram(
            dut,
            address=address,
            data=pattern
        )

        data = await read_ram(
            dut,
            address=address
        )

        assert data == pattern, (
            f"TEST 18 FAILED: "
            f"Expected 0x{pattern:04X}, "
            f"got 0x{data:04X}"
        )

    dut._log.info(
        "TEST 18 PASSED: Multiple 16-bit data patterns"
    )


    # ============================================================
    # TEST 19
    # LOW BYTE / HIGH BYTE
    # ============================================================

    await write_ram(
        dut,
        address=0x4000,
        data=0x00FF
    )

    data = await read_ram(
        dut,
        address=0x4000
    )

    assert data == 0x00FF

    await write_ram(
        dut,
        address=0x4000,
        data=0xFF00
    )

    data = await read_ram(
        dut,
        address=0x4000
    )

    assert data == 0xFF00

    dut._log.info(
        "TEST 19 PASSED: High-byte and low-byte testing"
    )


    # ============================================================
    # TEST 20
    # FINAL BOUNDARY CHECK
    # ============================================================

    boundary_tests = {
        0x0000: 0xAAAA,
        0x0001: 0xBBBB,
        0xFFFE: 0xCCCC,
        0xFFFF: 0xDDDD
    }

    for address, expected in boundary_tests.items():

        await write_ram(
            dut,
            address=address,
            data=expected
        )

    for address, expected in boundary_tests.items():

        data = await read_ram(
            dut,
            address=address
        )

        assert data == expected, (
            f"TEST 20 FAILED: "
            f"Address 0x{address:04X}, "
            f"Expected 0x{expected:04X}, "
            f"got 0x{data:04X}"
        )

    dut._log.info(
        "TEST 20 PASSED: RAM boundary addresses verified"
    )


    # ============================================================
    # COMPLETE
    # ============================================================

    dut._log.info("")
    dut._log.info("==========================================")
    dut._log.info("ALL 16-BIT RAM TESTS PASSED")
    dut._log.info("20 TEST GROUPS PASSED")
    dut._log.info("==========================================")

