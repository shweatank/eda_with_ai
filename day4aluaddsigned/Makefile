# Simulator Selection (default: icarus)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Design Source File
VERILOG_SOURCES += $(PWD)/adder_signed.sv

# Top-level Module & Python Test Module
TOPLEVEL = adder_signed
MODULE   = testbench_adder_signed

# Extra compile/sim arguments
COMPILE_ARGS += -g2012
SIM_ARGS     += -lxt2

# Include cocotb build rules
include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: show clean adder_signed all

# Optional: generate schematic using Yosys
show:
	yosys -p "read_verilog -sv adder_signed.sv; synth -top adder_signed; write_verilog -noattr adder_signed_netlist.v; show -format png -prefix adder_signed adder_signed"

# Run simulation (alias target)
adder_signed:
	$(MAKE) sim

# Combined target: run simulation + schematic
all:
	$(MAKE) sim
	$(MAKE) show

# Clean build artifacts
clean::
	rm -rf sim_build *.vcd *.xml *.png *.dot *.vvp *_netlist.v