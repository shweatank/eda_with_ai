# RTL Modules

Additional RTL building blocks with cocotb testbenches, in the same style as
`logic_gates/` (SystemVerilog design + Python/cocotb testbench + Makefile per module).

## Modules

| Module | Description |
|---|---|
| `mux2to1/` | 2:1 multiplexer |
| `mux4to1/` | 4:1 multiplexer |
| `half_adder/` | Half adder (sum, carry-out) |
| `full_adder/` | Full adder, built from two half adders |
| `ripple_carry_adder4/` | 4-bit ripple carry adder |
| `comparator4/` | 4-bit magnitude comparator (>, ==, <) |
| `d_flip_flop/` | D flip-flop with async active-low reset |
| `updown_counter4/` | 4-bit up/down counter with sync reset + enable |
| `sequence_detector_101/` | Moore FSM detecting overlapping "101" sequences |

## Requirements

- [Icarus Verilog](http://iverilog.icarus.com/) (`iverilog`) as the simulator
- Python 3.8+
- `cocotb` (`pip install cocotb`)

## Running a testbench

From inside any module folder:

```bash
make
```

This compiles the design with Icarus Verilog and runs the cocotb testbench
against it. Results (pass/fail per test) print to the console, and a
`results.xml` / `sim_build/` folder is generated (both should be gitignored).

To run all modules:

```bash
for d in */; do
  echo "== $d =="
  (cd "$d" && make)
done
```

## Adding a new module

1. Create a new folder: `rtl_modules/<module_name>/`
2. Add `design.sv` with your RTL
3. Add `test_<module_name>.py` with a cocotb testbench
4. Copy an existing `Makefile` and update `TOPLEVEL` and `MODULE`
5. Run `make` inside the folder to verify it passes
