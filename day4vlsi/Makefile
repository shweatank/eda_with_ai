# Simulator Selection (default: icarus)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Design Source File
VERILOG_SOURCES += $(PWD)/logic_or_and.sv

# Top-level Module & Python Test Module
TOPLEVEL = logic_or_and
MODULE   = testbench_logic_or_and

# Extra compile/sim arguments
COMPILE_ARGS += -g2012
SIM_ARGS     += -lxt2

# Include cocotb build rules
include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: show clean logic_or_and all

# Optional: generate schematic using Yosys
show:
	yosys -p "read_verilog -sv logic_or_and.sv; synth -top logic_or_and; show -format png -prefix logic_or_and logic_or_and"

# Run simulation (alias target)
logic_or_and:
	$(MAKE) sim

# Combined target: run simulation + schematic
all:
	$(MAKE) sim
	$(MAKE) show

# Clean build artifacts
clean::
	rm -rf sim_build *.vcd *.xml *.png *.dot *.vvp *_netlist.v