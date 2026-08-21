# Simulator Selection (default: icarus)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Design Source File
VERILOG_SOURCES += $(PWD)/comparator.sv

# Top-level Module & Python Test Module
TOPLEVEL = comparator
MODULE   = testbench_comparator

# Extra compile/sim arguments
COMPILE_ARGS += -g2012
SIM_ARGS     += -lxt2

# Include cocotb build rules
include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: show clean comparator all

# Optional: generate schematic using Yosys
show:
	yosys -p "read_verilog -sv comparator.sv; synth -top comparator; write_verilog -noattr comparator_netlist.v; show -format png -prefix comparator comparator"

# Run simulation (alias target)
comparator:
	$(MAKE) sim

# Combined target: run simulation + schematic
all:
	$(MAKE) sim
	$(MAKE) show
# Clean build artifacts
clean::
	rm -rf sim_build *.vcd *.xml *.png *.dot *.vvp *_netlist.v
