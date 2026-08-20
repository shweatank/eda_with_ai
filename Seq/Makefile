# Simulator
SIM ?= icarus

# HDL language
TOPLEVEL_LANG ?= verilog

# RTL source
VERILOG_SOURCES += $(PWD)/adder.sv

# Top-level HDL module
TOPLEVEL = adder

# Cocotb Python test
MODULE = test_add


# Targets
.PHONY: all sim synth netlist show-netlist show-circuit wave clean-all


# Default target
all: sim synth netlist show-circuit


# Yosys synthesis
synth:
	yosys -p "read_verilog -sv adder.sv; hierarchy -top adder; proc; opt; techmap; opt; write_verilog -noattr adder_netlist.v"


# Check that netlist was generated
netlist: synth
	@test -f adder_netlist.v
	@echo "SUCCESS: adder_netlist.v generated"


# Display netlist
show-netlist: synth
	cat adder_netlist.v


# Generate circuit diagram
show-circuit:
	yosys -p "read_verilog -sv adder.sv; hierarchy -top adder; proc; opt; techmap; opt; show -format png -prefix adder"


# Open waveform
wave: sim
	gtkwave adder.vcd


# Clean generated files
clean-all:
	$(MAKE) clean
	rm -f adder.vcd
	rm -f adder_netlist.v
	rm -f adder.png
	rm -f results.xml
	rm -rf sim_build/


# Cocotb simulation rules
include $(shell cocotb-config --makefiles)/Makefile.sim