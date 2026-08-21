# Simulator Selection (default: icarus)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Design Source File
VERILOG_SOURCES += $(PWD)/multiplexer.sv

# Top-level Module & Python Test Module
TOPLEVEL = mux4
MODULE   = testbench_multiplexer

# Extra compile/sim arguments
COMPILE_ARGS += -g2012
SIM_ARGS     += -lxt2

# Include cocotb build rules
include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: show clean mux4 all

# Optional: generate schematic using Yosys
show:
	yosys -p "read_verilog -sv multiplexer.sv; synth -top mux4; write_verilog -noattr mux4_netlist.v; show -format png -prefix mux4 mux4"

# Run simulation (alias target)
mux4:
	$(MAKE) sim

# Combined target: run simulation + schematic
all:
	$(MAKE) sim
	$(MAKE) show

# Clean build artifacts
clean::
	rm -rf sim_build *.vcd *.xml *.png *.dot *.vvp *_netlist.v