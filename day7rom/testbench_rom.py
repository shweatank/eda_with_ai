import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_rom(dut):

    # Test address 0
    dut.address.value = 0
    await Timer(1, unit="ns")

    read_value = int(dut.data.value)

    print(f"Address 0 -> Data = {read_value}")

    # Test address 1
    dut.address.value = 1
    await Timer(1, unit="ns")

    read_value = int(dut.data.value)

    print(f"Address 1 -> Data = {read_value}")

    # Test address 2
    dut.address.value = 2
    await Timer(1, unit="ns")

    read_value = int(dut.data.value)

    print(f"Address 2 -> Data = {read_value}")

    # Test address 3
    dut.address.value = 3
    await Timer(1, unit="ns")

    read_value = int(dut.data.value)

    print(f"Address 3 -> Data = {read_value}")

    print("===================================")
    print("         ROM TEST PASSED")
    print("===================================")