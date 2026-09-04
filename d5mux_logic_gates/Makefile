# Simulator Selection (default: icarus)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Design Source File
VERILOG_SOURCES += $(PWD)/logic_gates.sv

# Top-level Module & Python Test Module
TOPLEVEL = logic_gates
MODULE   = testbench_logic_gates

# Extra compile/sim arguments
COMPILE_ARGS += -g2012
SIM_ARGS     += -lxt2

# Include cocotb build rules
include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: show clean logic_gates all

# Optional: generate schematic using Yosys
show:
	yosys -p "read_verilog -sv logic_gates.sv; synth -top logic_gates; write_verilog -noattr logic_gates_netlist.v; show -format png -prefix logic_gates logic_gates"

# Run simulation (alias target)
logic_gates:
	$(MAKE) sim

# Combined target: run simulation + schematic
all:
	$(MAKE) sim
	$(MAKE) show

# Clean build artifacts
clean::
	rm -rf sim_build *.vcd *.xml *.png *.dot *.vvp *_netlist.v