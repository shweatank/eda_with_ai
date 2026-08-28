# APB UART Peripheral

Industry-style RTL verification project combining an APB4-lite register interface with UART TX/RX, FIFOs, interrupt status, error flags, assertions, and artifact generation.

Registers: `0x00 TX`, `0x04 RX`, `0x08 STATUS`, `0x0C CONTROL`.

Run with the workspace environment:

```sh
source /home/mirafra/venv/bin/activate
make
make DATA_WIDTH=8 FIFO_DEPTH=8
make artifacts
```
