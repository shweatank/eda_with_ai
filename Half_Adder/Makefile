# Simulator
SIM ?= icarus

# HDL language
TOPLEVEL_LANG ?= verilog

# RTL source
VERILOG_SOURCES += $(PWD)/half_adder.sv

# Top-level HDL module
TOPLEVEL = half_adder

# Cocotb Python test
MODULE = test_half_adder


# Targets
.PHONY: all sim synth netlist show-netlist show-circuit wave clean-all


# Default target
all: sim synth netlist show-circuit


# Yosys synthesis
synth:
	yosys -p "read_verilog -sv half_adder.sv; hierarchy -top half_adder; proc; opt; techmap; opt; write_verilog -noattr half_adder_netlist.v"


# Check that netlist was generated
netlist: synth
	@test -f half_adder_netlist.v
	@echo "SUCCESS: half_adder_netlist.v generated"


# Display netlist
show-netlist: synth
	cat half_adder_netlist.v


# Generate circuit diagram
show-circuit:
	yosys -p "read_verilog -sv half_adder.sv; hierarchy -top half_adder; proc; opt; techmap; opt; show -format png -prefix half_adder"


# Open waveform
wave: sim
	gtkwave half_adder.vcd


# Clean generated files
clean-all:
	$(MAKE) clean
	rm -f half_adder.vcd
	rm -f half_adder_netlist.v
	rm -f half_adder.png
	rm -f results.xml
	rm -rf sim_build/


# Cocotb simulation rules
include $(shell cocotb-config --makefiles)/Makefile.sim