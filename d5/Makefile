# Simulator Selection (default: icarus)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Design Source File
VERILOG_SOURCES += $(PWD)/mux_if.sv

# Top-level Module & Python Test Module
TOPLEVEL = mux_if
MODULE   = testbench_mux_if

# Extra compile/sim arguments
COMPILE_ARGS += -g2012
SIM_ARGS     += -lxt2

# Include cocotb build rules
include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: show clean mux_if all

# Optional: generate schematic using Yosys
show:
	yosys -p "read_verilog -sv mux_if.sv; synth -top mux_if; write_verilog -noattr mux_if_netlist.v; show -format png -prefix mux_if mux_if"

# Run simulation (alias target)
mux_if:
	$(MAKE) sim

# Combined target: run simulation + schematic
all:
	$(MAKE) sim
	$(MAKE) show

# Clean build artifacts
clean::
	rm -rf sim_build *.vcd *.xml *.png *.dot *.vvp *_netlist.v