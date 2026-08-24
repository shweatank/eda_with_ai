# Simulator
SIM ?= icarus

# HDL language
TOPLEVEL_LANG ?= verilog

# RTL source
VERILOG_SOURCES += $(PWD)/arith_unit.sv

# Top-level HDL module
TOPLEVEL = arith_unit

# Cocotb Python test
MODULE = test_arith

# Parameters (can be overridden on command line)
WIDTH ?= 4

# Targets
.PHONY: all sim synth netlist show-netlist show-circuit wave clean-all

# Default target
all: sim synth netlist show-circuit

# Yosys synthesis
synth:
	yosys -p "read_verilog -sv arith_unit.sv; hierarchy -top arith_unit; proc; opt; techmap; opt; write_verilog -noattr arith_unit_netlist.v"

# Check that netlist was generated
netlist: synth
	@test -f arith_unit_netlist.v
	@echo "SUCCESS: arith_unit_netlist.v generated"

# Display netlist
show-netlist: synth
	cat arith_unit_netlist.v

# Generate circuit diagram (requires Graphviz for PNG)
show-circuit:
	yosys -p "read_verilog -sv arith_unit.sv; hierarchy -top arith_unit; proc; opt; techmap; opt; write_json arith_unit.json"
	netlistsvg arith_unit.json -o arith_unit.svg


# Run simulation with Cocotb
sim:
	@echo "Compiling with WIDTH=$(WIDTH)"
	mkdir -p sim_build
	iverilog -g2012 -o sim_build/sim.vvp -D WIDTH=$(WIDTH) -s $(TOPLEVEL) $(VERILOG_SOURCES)
	vvp sim_build/sim.vvp

# Open waveform
wave: sim
	gtkwave arith_unit.vcd

# Clean generated files
clean-all:
	$(MAKE) clean
	rm -f arith_unit.vcd
	#rm -f arith_unit_netlist.v
	#rm -f arith_unit.png
	rm -f results.xml
	rm -f *.dot
	rm -f *.new
	rm -rf sim_build/

# Cocotb simulation rules
include $(shell cocotb-config --makefiles)/Makefile.sim
