# Simulator Selection (default: icarus)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Design Source File
VERILOG_SOURCES += $(PWD)/adder.sv

# Top-level Module & Python Test Module
TOPLEVEL = adder
MODULE   = testbench_adder

# Extra compile/sim arguments
COMPILE_ARGS += -g2012
SIM_ARGS     += -lxt2

# Include cocotb build rules
include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: show clean adder all

# Optional: generate schematic using Yosys
show:
	yosys -p "read_verilog -sv adder.sv; synth -top adder; write_verilog -noattr adder_netlist.v; show -format png -prefix adder adder"

# Run simulation (alias target)
adder:
	$(MAKE) sim

# Combined target: run simulation + schematic
all:
	$(MAKE) sim
	$(MAKE) show

# Clean build artifacts
clean::
	rm -rf sim_build *.vcd *.xml *.png *.dot *.vvp *_netlist.v