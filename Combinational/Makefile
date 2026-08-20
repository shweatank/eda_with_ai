# Simulator
SIM ?= icarus

# HDL language
TOPLEVEL_LANG ?= verilog

# RTL source
VERILOG_SOURCES += $(PWD)/xnor_gate.sv

# Top-level HDL module
TOPLEVEL = xnor_gate

# Cocotb Python test
MODULE = test_xnor


# Targets
.PHONY: all sim synth netlist show-netlist show-circuit wave clean-all


# Default target
all: sim synth netlist show-circuit


# Yosys synthesis
synth:
	yosys -p "read_verilog -sv xnor_gate.sv; hierarchy -top xnor_gate; proc; opt; techmap; opt; write_verilog -noattr xnor_gate_netlist.v"


# Check that netlist was generated
netlist: synth
	@test -f xnor_gate_netlist.v
	@echo "SUCCESS: xnor_gate_netlist.v generated"


# Display netlist
show-netlist: synth
	cat xnor_gate_netlist.v


# Generate circuit diagram
show-circuit:
	yosys -p "read_verilog -sv xnor_gate.sv; hierarchy -top xnor_gate; proc; opt; techmap; opt; show -format png -prefix xnor_gate"


# Open waveform
wave: sim
	gtkwave xnor_gate.vcd


# Clean generated files
clean-all:
	$(MAKE) clean
	rm -f xnor_gate.vcd
	rm -f xnor_gate_netlist.v
	rm -f xnor_gate.png
	rm -f results.xml
	rm -rf sim_build/


# Cocotb simulation rules
include $(shell cocotb-config --makefiles)/Makefile.sim