import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def arithmetic(dut):
    # ==================== ADD ====================
    dut.a.value = 5
    dut.b.value = 10
    await Timer(1, unit="ns")
    assert dut.sum.value == 15
    print("PASS: ADD 5 + 10 = 15")

    dut.a.value = 0
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.sum.value == 0
    print("PASS: ADD 0 + 0 = 0")

    dut.a.value = 255
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.sum.value == 255
    print("PASS: ADD 255 + 0 = 255")

    dut.a.value = 255
    dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.sum.value == 0
    print("PASS: ADD 255 + 1 = 0 (overflow)")

    dut.a.value = 128
    dut.b.value = 128
    await Timer(1, unit="ns")
    assert dut.sum.value == 0
    print("PASS: ADD 128 + 128 = 0 (overflow)")

    dut.a.value = 255
    dut.b.value = 255
    await Timer(1, unit="ns")
    assert dut.sum.value == 254
    print("PASS: ADD 255 + 255 = 254 (max overflow)")

    # ==================== SUBTRACT ====================
    dut.a.value = 10
    dut.b.value = 5
    await Timer(1, unit="ns")
    assert dut.diff.value == 5
    print("PASS: SUB 10 - 5 = 5")

    dut.a.value = 7
    dut.b.value = 7
    await Timer(1, unit="ns")
    assert dut.diff.value == 0
    print("PASS: SUB 7 - 7 = 0")

    dut.a.value = 0
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.diff.value == 0
    print("PASS: SUB 0 - 0 = 0")

    dut.a.value = 255
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.diff.value == 255
    print("PASS: SUB 255 - 0 = 255")

    dut.a.value = 0
    dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.diff.value == 255
    print("PASS: SUB 0 - 1 = 255 (borrow/underflow)")

    dut.a.value = 0
    dut.b.value = 255
    await Timer(1, unit="ns")
    assert dut.diff.value == 1
    print("PASS: SUB 0 - 255 = 1 (max borrow/underflow)")

    # ==================== MULTIPLY ====================
    dut.a.value = 5
    dut.b.value = 6
    await Timer(1, unit="ns")
    assert dut.product.value == 30
    print("PASS: MUL 5 * 6 = 30")

    dut.a.value = 200
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert dut.product.value == 0
    print("PASS: MUL 200 * 0 = 0")

    dut.a.value = 123
    dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.product.value == 123
    print("PASS: MUL 123 * 1 = 123")

    dut.a.value = 3
    dut.b.value = 4
    await Timer(1, unit="ns")
    assert dut.product.value == 12
    print("PASS: MUL 3 * 4 = 12")

    dut.a.value = 255
    dut.b.value = 255
    await Timer(1, unit="ns")
    assert dut.product.value == 65025
    print("PASS: MUL 255 * 255 = 65025 (max product, no overflow)")

    dut.a.value = 255
    dut.b.value = 100
    await Timer(1, unit="ns")
    assert dut.product.value == 25500
    print("PASS: MUL 255 * 100 = 25500")

    # ==================== DIVIDE ====================
    dut.a.value = 20
    dut.b.value = 4
    await Timer(1, unit="ns")
    assert dut.quotient.value == 5
    assert dut.remainder.value == 0
    print("PASS: DIV 20 / 4 = 5 remainder 0")

    dut.a.value = 17
    dut.b.value = 5
    await Timer(1, unit="ns")
    assert dut.quotient.value == 3
    assert dut.remainder.value == 2
    print("PASS: DIV 17 / 5 = 3 remainder 2")

    dut.a.value = 3
    dut.b.value = 10
    await Timer(1, unit="ns")
    assert dut.quotient.value == 0
    assert dut.remainder.value == 3
    print("PASS: DIV 3 / 10 = 0 remainder 3")

    dut.a.value = 0
    dut.b.value = 7
    await Timer(1, unit="ns")
    assert dut.quotient.value == 0
    assert dut.remainder.value == 0
    print("PASS: DIV 0 / 7 = 0 remainder 0")

    dut.a.value = 200
    dut.b.value = 1
    await Timer(1, unit="ns")
    assert dut.quotient.value == 200
    assert dut.remainder.value == 0
    print("PASS: DIV 200 / 1 = 200 remainder 0")

    dut.a.value = 255
    dut.b.value = 255
    await Timer(1, unit="ns")
    assert dut.quotient.value == 1
    assert dut.remainder.value == 0
    print("PASS: DIV 255 / 255 = 1 remainder 0")

    dut.a.value = 10
    dut.b.value = 0
    await Timer(1, unit="ns")
    assert str(dut.quotient.value).upper() == "XXXXXXXX"
    assert str(dut.remainder.value).upper() == "XXXXXXXX"
    print("PASS: DIV 10 / 0 -> quotient and remainder are undefined (X), as expected")
