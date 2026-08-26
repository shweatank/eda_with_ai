#!/usr/bin/env bash
set -euo pipefail

echo "======================================"
echo "       AND + FF STA LAB"
echo "======================================"

echo "[1] Creating build directory"
mkdir -p build

echo "[2] Running Cocotb simulation"
make

echo "[3] Running Yosys synthesis"
yosys scripts/synth.ys

echo "[4] Checking synthesized netlist"
test -f build/and_ff_netlist.v
echo "Netlist generated successfully"

echo "[5] Running OpenSTA"
command -v sta >/dev/null || { echo "ERROR: OpenSTA executable 'sta' was not found" >&2; exit 1; }
test -f libraries/sky130_fd_sc_hd__tt_025C_1v80.lib || {
    echo "ERROR: Missing Sky130 Liberty file in libraries/" >&2
    exit 1
}
sta -exit scripts/sta.tcl

echo "======================================"
echo "       COMPLETE FLOW FINISHED"
echo "======================================"
