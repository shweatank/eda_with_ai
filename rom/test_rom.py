import cocotb

from cocotb.triggers import Timer


# ================================================================
# READ FUNCTION
# ================================================================

async def read_rom(dut, address):

    dut.address.value = address

    # ROM is asynchronous, so wait for combinational propagation
    await Timer(1, units="ns")

    return int(dut.data.value)


# ================================================================
# TEST
# ================================================================

@cocotb.test()
async def test_rom(dut):

    dut._log.info("==========================================")
    dut._log.info("ROM TEST STARTED")
    dut._log.info("==========================================")


    # ============================================================
    # TEST 1
    # ADDRESS 0
    # ============================================================

    data = await read_rom(
        dut,
        address=0x0
    )

    assert data == 0x11, (
        f"TEST 1 FAILED: Expected 0x11, got 0x{data:02X}"
    )

    dut._log.info(
        "TEST 1 PASSED: Address 0x0 = 0x11"
    )


    # ============================================================
    # TEST 2
    # ADDRESS 1
    # ============================================================

    data = await read_rom(
        dut,
        address=0x1
    )

    assert data == 0x22, (
        f"TEST 2 FAILED: Expected 0x22, got 0x{data:02X}"
    )

    dut._log.info(
        "TEST 2 PASSED: Address 0x1 = 0x22"
    )


    # ============================================================
    # TEST 3
    # ADDRESS 2
    # ============================================================

    data = await read_rom(
        dut,
        address=0x2
    )

    assert data == 0x33, (
        f"TEST 3 FAILED: Expected 0x33, got 0x{data:02X}"
    )

    dut._log.info(
        "TEST 3 PASSED: Address 0x2 = 0x33"
    )


    # ============================================================
    # TEST 4
    # ADDRESS 3
    # ============================================================

    data = await read_rom(
        dut,
        address=0x3
    )

    assert data == 0x44, (
        f"TEST 4 FAILED: Expected 0x44, got 0x{data:02X}"
    )

    dut._log.info(
        "TEST 4 PASSED: Address 0x3 = 0x44"
    )


    # ============================================================
    # TEST 5
    # ADDRESS 4
    # ============================================================

    data = await read_rom(
        dut,
        address=0x4
    )

    assert data == 0x55, (
        f"TEST 5 FAILED: Expected 0x55, got 0x{data:02X}"
    )

    dut._log.info(
        "TEST 5 PASSED: Address 0x4 = 0x55"
    )


    # ============================================================
    # TEST 6
    # ADDRESS 5
    # ============================================================

    data = await read_rom(
        dut,
        address=0x5
    )

    assert data == 0x66, (
        f"TEST 6 FAILED: Expected 0x66, got 0x{data:02X}"
    )

    dut._log.info(
        "TEST 6 PASSED: Address 0x5 = 0x66"
    )


    # ============================================================
    # TEST 7
    # ADDRESS 6
    # ============================================================

    data = await read_rom(
        dut,
        address=0x6
    )

    assert data == 0x77, (
        f"TEST 7 FAILED: Expected 0x77, got 0x{data:02X}"
    )

    dut._log.info(
        "TEST 7 PASSED: Address 0x6 = 0x77"
    )


    # ============================================================
    # TEST 8
    # ADDRESS 7
    # ============================================================

    data = await read_rom(
        dut,
        address=0x7
    )

    assert data == 0x88, (
        f"TEST 8 FAILED: Expected 0x88, got 0x{data:02X}"
    )

    dut._log.info(
        "TEST 8 PASSED: Address 0x7 = 0x88"
    )


    # ============================================================
    # TEST 9
    # CHECK ALL ROM LOCATIONS
    # ============================================================

    expected_data = {
        0x0: 0x11,
        0x1: 0x22,
        0x2: 0x33,
        0x3: 0x44,
        0x4: 0x55,
        0x5: 0x66,
        0x6: 0x77,
        0x7: 0x88
    }

    for address, expected in expected_data.items():

        data = await read_rom(
            dut,
            address=address
        )

        assert data == expected, (
            f"TEST 9 FAILED: "
            f"Address 0x{address:X}: "
            f"Expected 0x{expected:02X}, "
            f"got 0x{data:02X}"
        )

    dut._log.info(
        "TEST 9 PASSED: All ROM locations verified"
    )


    # ============================================================
    # TEST 10
    # ADDRESS SEQUENCE
    # ============================================================

    for address in range(8):

        data = await read_rom(
            dut,
            address=address
        )

        expected = 0x11 + (address * 0x11)

        assert data == expected, (
            f"TEST 10 FAILED: "
            f"Address {address}: "
            f"Expected 0x{expected:02X}, "
            f"got 0x{data:02X}"
        )

    dut._log.info(
        "TEST 10 PASSED: Sequential address test"
    )


    # ============================================================
    # TEST 11
    # REVERSE ADDRESS SEQUENCE
    # ============================================================

    for address in range(7, -1, -1):

        data = await read_rom(
            dut,
            address=address
        )

        expected = 0x11 + (address * 0x11)

        assert data == expected, (
            f"TEST 11 FAILED: "
            f"Address {address}: "
            f"Expected 0x{expected:02X}, "
            f"got 0x{data:02X}"
        )

    dut._log.info(
        "TEST 11 PASSED: Reverse address test"
    )


    # ============================================================
    # TEST 12
    # DATA PERSISTENCE
    # ============================================================

    for address, expected in expected_data.items():

        data = await read_rom(
            dut,
            address=address
        )

        assert data == expected

    dut._log.info(
        "TEST 12 PASSED: ROM data remains fixed"
    )


    # ============================================================
    # TEST 13
    # BOUNDARY ADDRESS 0
    # ============================================================

    data = await read_rom(
        dut,
        address=0x0
    )

    assert data == 0x11

    dut._log.info(
        "TEST 13 PASSED: Minimum address 0x0"
    )


    # ============================================================
    # TEST 14
    # MAXIMUM ADDRESS 7
    # ============================================================

    data = await read_rom(
        dut,
        address=0x7
    )

    assert data == 0x88

    dut._log.info(
        "TEST 14 PASSED: Maximum address 0x7"
    )


    # ============================================================
    # TEST 15
    # ALTERNATING ADDRESS ACCESS
    # ============================================================

    addresses = [0, 7, 1, 6, 2, 5, 3, 4]

    for address in addresses:

        data = await read_rom(
            dut,
            address=address
        )

        expected = 0x11 + (address * 0x11)

        assert data == expected, (
            f"TEST 15 FAILED: "
            f"Address {address}: "
            f"Expected 0x{expected:02X}, "
            f"got 0x{data:02X}"
        )

    dut._log.info(
        "TEST 15 PASSED: Random address access"
    )


    # ============================================================
    # COMPLETE
    # ============================================================

    dut._log.info("")
    dut._log.info("==========================================")
    dut._log.info("ALL ROM TESTS PASSED")
    dut._log.info("15 TEST GROUPS PASSED")
    dut._log.info("==========================================")