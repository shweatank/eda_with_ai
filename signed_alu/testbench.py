import cocotb
from cocotb.triggers import Timer


def signed_8bit(value):
    value &= 0xFF

    if value & 0x80:
        return value - 256

    return value


@cocotb.test()
async def test_alu(dut):

    test_cases = [
      

        (0,      0,    0),
        (10,     20,   0),
        (-10,    5,    0),
        (-10,   -5,    0),

     
        (127,    1,    0),
        (-128,  -1,    0),


       

        (10,     5,    1),
        (5,      10,   1),
        (-10,    5,    1),
        (10,    -5,    1),
        (-10,   -5,    1),

     
        (127,   -1,    1),
        (-128,   1,    1),



        (5,      10,   2),
        (10,     -5,   2),
        (-10,    -5,   2),
        (3,       4,   2),

        (50,      3,   2),
        (-50,     3,   2),



        (10,      5,   3),
        (10,     -5,   3),
        (-10,     5,   3),
        (-10,    -5,   3),
        (20,      3,   3),

    
        (10,      0,   3),
    ]


    for A, B, OP in test_cases:

        # Send inputs to Verilog
        dut.A.value = A & 0xFF
        dut.B.value = B & 0xFF
        dut.OP.value = OP

        # Wait for combinational logic
        await Timer(1, unit="ns")


        if OP == 0:
            expected = A + B

        elif OP == 1:
            expected = A - B

        elif OP == 2:
            expected = A * B

        elif OP == 3:
            if B == 0:
                expected = 0
            else:
                expected = int(A / B)


    

        expected_result = signed_8bit(expected)



        if OP == 3 and B == 0:

            # Division by zero
            expected_overflow = True

        else:

            expected_overflow = (
                expected < -128 or expected > 127
            )

        actual_result = signed_8bit(
            int(dut.Result.value)
        )

        actual_overflow = int(
            dut.Overflow.value
        )


        # =================================
        # Operation name
        # =================================

        if OP == 0:
            operation = "ADD"

        elif OP == 1:
            operation = "SUB"

        elif OP == 2:
            operation = "MUL"

        else:
            operation = "DIV"


        print(
            f"{operation}: "
            f"A={A:4}, "
            f"B={B:4} "
            f"-> Result={actual_result:4}, "
            f"Expected={expected_result:4}, "
            f"Overflow={actual_overflow}"
        )

        assert actual_result == expected_result

        assert actual_overflow == expected_overflow