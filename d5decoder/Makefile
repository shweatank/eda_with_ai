# Simulator Selection (default: icarus)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Design Source File
VERILOG_SOURCES += $(PWD)/decoder_2to4.sv

# Top-level Module & Python Test Module
TOPLEVEL = decoder_2to4
MODULE   = testbench_decoder_2to4

# Extra compile/sim arguments
COMPILE_ARGS += -g2012
SIM_ARGS     += -lxt2

# Include cocotb build rules
include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: show clean decoder_2to4 all

# Optional: generate schematic using Yosys
show:
	yosys -p "read_verilog -sv decoder_2to4.sv; synth -top decoder_2to4; write_verilog -noattr decoder_2to4_netlist.v; show -format png -prefix decoder_2to4 decoder_2to4"

# Run simulation (alias target)
decoder_2to4:
	$(MAKE) sim

# Combined target: run simulation + schematic
all:
	$(MAKE) sim
	$(MAKE) show

# Clean build artifacts
clean::
	rm -rf sim_build *.vcd *.xml *.png *.dot *.vvp *_netlist.v