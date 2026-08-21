# Simulator Selection (default: icarus)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Design Source File
VERILOG_SOURCES += $(PWD)/single_bit_mux.sv

# Top-level Module & Python Test Module
TOPLEVEL = mux2
MODULE   = testbench_singlebit_mux

# Extra compile/sim arguments
COMPILE_ARGS += -g2012
SIM_ARGS     += -lxt2

# Include cocotb build rules
include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: show clean mux_singlebit all

# Optional: generate schematic using Yosys
show:
	yosys -p "read_verilog -sv single_bit_mux.sv; synth -top mux2; write_verilog -noattr single_bit_mux_netlist.v; show -format png -prefix single_bit_mux mux2"

# Run simulation (alias target)
mux_singlebit:
	$(MAKE) sim

# Combined target: run simulation + schematic
all:
	$(MAKE) sim
	$(MAKE) show

# Clean build artifacts
clean::
	rm -rf sim_build *.vcd *.xml *.png *.dot *.vvp *_netlist.v