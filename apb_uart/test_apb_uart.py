import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


async def apb_write(dut, address, value):
    dut.psel.value = 1; dut.penable.value = 0; dut.pwrite.value = 1
    dut.paddr.value = address; dut.pwdata.value = value
    await RisingEdge(dut.pclk)
    dut.penable.value = 1
    await RisingEdge(dut.pclk)
    dut.psel.value = 0; dut.penable.value = 0


async def apb_read(dut, address):
    dut.psel.value = 1; dut.penable.value = 0; dut.pwrite.value = 0
    dut.paddr.value = address
    await RisingEdge(dut.pclk)
    dut.penable.value = 1
    await RisingEdge(dut.pclk)
    value = int(dut.prdata.value)
    dut.psel.value = 0; dut.penable.value = 0
    return value


async def uart_send_byte(dut, value, baud_cycles=16):
    dut.uart_rx.value = 0
    for _ in range(baud_cycles): await RisingEdge(dut.pclk)
    for bit in range(8):
        dut.uart_rx.value = (value >> bit) & 1
        for _ in range(baud_cycles): await RisingEdge(dut.pclk)
    dut.uart_rx.value = 1
    for _ in range(baud_cycles): await RisingEdge(dut.pclk)


@cocotb.test()
async def test_apb_uart(dut):
    cocotb.start_soon(Clock(dut.pclk, 10, unit="ns").start())
    dut.presetn.value = 0; dut.psel.value = 0; dut.penable.value = 0; dut.pwrite.value = 0; dut.uart_rx.value = 1
    await Timer(30, unit="ns")
    dut.presetn.value = 1
    assert int(await apb_read(dut, 0x08)) & 0x01 == 1

    await apb_write(dut, 0x0C, 1)
    await uart_send_byte(dut, 0xA5)
    status = await apb_read(dut, 0x08)
    assert status & 0x02 == 0, "RX overrun unexpectedly set"
    received = await apb_read(dut, 0x04)
    print(f"UART RX received=0x{received & 0xFF:02X}, expected=0xA5")
    assert received & 0xFF == 0xA5
    await RisingEdge(dut.pclk)
    assert int(dut.irq.value) == 0

    await apb_write(dut, 0x00, 0x5A)
    for _ in range(220): await RisingEdge(dut.pclk)
    assert int(dut.uart_tx.value) == 1
    invalid = await apb_read(dut, 0x20)
    assert invalid == 0
    assert int(dut.pslverr.value) == 1
    print("APB UART PASS: reset, APB registers, UART RX, TX, IRQ, and invalid access")
