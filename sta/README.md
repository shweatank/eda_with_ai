# AND + flip-flop STA lab

This project verifies a registered AND gate with Cocotb, synthesizes it with
Yosys, and performs setup/hold timing analysis with OpenSTA.

## Prerequisites

Install Python 3, Cocotb, Icarus Verilog, Yosys, GNU Make, OpenSTA, and a real
Sky130 Liberty timing library. Install the Python package with:

```sh
python3 -m pip install -r requirements.txt
```

Place the characterized library at:

```
libraries/sky130_fd_sc_hd__tt_025C_1v80.lib
```

## Run the stages

```sh
make
mkdir -p build && yosys scripts/synth.ys
sta -exit scripts/sta.tcl
```

Or run `./run_flow.sh` after all prerequisites are installed.

> The supplied Yosys script is intentionally generic and produces a
> technology-independent netlist. A real ASIC STA flow must map with
> `dfflibmap` and `abc -liberty` against the same Sky130 Liberty file before
> OpenSTA; otherwise OpenSTA cannot time the generic internal cells.
