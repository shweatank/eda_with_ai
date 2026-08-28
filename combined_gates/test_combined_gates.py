import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_all_gates_in_one_case(dut):
    width = len(dut.a)
    mask = (1 << width) - 1
    test_vectors = [
        (0x00, 0x00, 0x00),
        (0xFF, 0x00, 0xAA),
        (0xFF, 0xFF, 0x55),
        (0xAA, 0x55, 0x0F),
        (0x0F, 0xF0, 0xF0),
        (0x3C, 0xA5, 0xC3),
    ]

    for a, b, c in test_vectors:
        a &= mask
        b &= mask
        c &= mask
        dut.a.value = a
        dut.b.value = b
        dut.c.value = c
        await Timer(1, unit="ns")

        operations = [
            a & b,
            a | b,
            a ^ b,
            ~(a & b),
            ~(a | b),
            ~c,
            ~(a ^ b),
            (a & b) | c,
        ]
        expected_value = sum(((operations[index % 8] >> index) & 1) << index for index in range(width))
        actual_value = int(dut.y.value)
        digits = (width + 3) // 4
        print(f"a=0x{a:0{digits}X} b=0x{b:0{digits}X} c=0x{c:0{digits}X} expected y=0x{expected_value:0{digits}X} actual y=0x{actual_value:0{digits}X}")
        assert actual_value == expected_value, f"Inputs a={a}, b={b}, c={c}: {actual_value} != {expected_value}"

    print(f"ALL COMBINED {width}-BIT GATES PASSED: {len(test_vectors)} vector patterns")
