# Parameterized Synchronous FIFO

A synchronous FIFO with configurable `DATA_WIDTH` and `FIFO_DEPTH`.

## Run verification

```sh
make DATA_WIDTH=8 FIFO_DEPTH=8
make DATA_WIDTH=16 FIFO_DEPTH=16
make DATA_WIDTH=32 FIFO_DEPTH=32
make artifacts
```

The cocotb test verifies reset, FIFO ordering, full behavior, overflow, empty behavior, and underflow.
