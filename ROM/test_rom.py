import cocotb
from cocotb.triggers import Timer

# Expected ROM contents, indexed by address
ROM_CONTENTS = {
    0: 0x11,
    1: 0x22,
    2: 0x33,
    3: 0x44,
    4: 0x55,
    5: 0x66,
    6: 0x77,
    7: 0x88,
}

@cocotb.test()
async def test_rom(dut):
    # Test every address individually
    for addr, expected in ROM_CONTENTS.items():
        dut.address.value = addr
        await Timer(1, unit="ns")
        assert dut.data.value == expected, \
            f"FAIL: address={addr} -> got 0x{int(dut.data.value):02X}, expected 0x{expected:02X}"
        print(f"PASS: address={addr} -> data=0x{expected:02X}")

    # Re-check address 0 again after cycling through all others
    # (confirms ROM output correctly changes back, not "stuck" on last value)
    dut.address.value = 0
    await Timer(1, unit="ns")
    assert dut.data.value == 0x11
    print("PASS: address=0 (re-checked) -> data=0x11")

    # Sweep through all addresses in reverse order too, as an extra sanity check
    for addr in reversed(range(8)):
        dut.address.value = addr
        await Timer(1, unit="ns")
        expected = ROM_CONTENTS[addr]
        assert dut.data.value == expected, \
            f"FAIL (reverse): address={addr} -> got 0x{int(dut.data.value):02X}, expected 0x{expected:02X}"
        print(f"PASS (reverse): address={addr} -> data=0x{expected:02X}")
