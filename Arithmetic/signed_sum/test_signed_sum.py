# import cocotb
# from cocotb.triggers import Timer

# @cocotb.test()
# async def test_or_gate(dut):

#     # 1.Test 8 + 9 = 17
#     dut.a.value = 8
#     dut.b.value = 9

#     await Timer(1, unit="ns")

#     assert dut.sum.value == 17

#     print("PASS: 8 + 9 = 17")


import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_signed_sum(dut):
    test_vectors = [
        (-1, -1, -2),
        (0, 1, 1),
        (127, -127, 0),
        (-127,-127, -254),
        (127, 1, 128),
        (-128, -1, -129)
    ]

    for a_val, b_val, expected in test_vectors:
        dut.a.value = a_val
        dut.b.value = b_val
        await Timer(1, unit="ns")
        assert int(dut.sum.value.signed_integer) == expected, f"Expected {expected}, got {int(dut.sum.value.signed_integer)}"
        print(f"PASS: {a_val} + {b_val} = {expected}") 

