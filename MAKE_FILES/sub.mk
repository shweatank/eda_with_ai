SIM = icarus

COMPILE_ARGS += -g2012

VERILOG_SOURCES = $(PWD)/rtl/four_bit_sub.sv

TOPLEVEL = four_bit_sub

MODULE = tests.test_sub

WAVES = 1
.PHONY: all synth netlist netlist show-netlist show-circuit wave clean-all
all: sim synth netlist show-circuit


# Yosys synthesis
synth:
	yosys -p "read_verilog -sv rtl/four_bit_sub.sv; hierarchy -top four_bit_sub; proc; opt; techmap; opt; write_verilog -noattr sub_netlist.v"


# Check that netlist was generated
netlist: synth
	@test -f sub_netlist.v
	@echo "SUCCESS: sub_netlist.v generated"


# Display netlist
show-netlist: synth
	cat sub_netlist.v


# Generate circuit diagram
show-circuit:
	yosys -p "read_verilog -sv rtl/four_bit_sub.sv; hierarchy -top four_bit_sub; proc; opt; techmap; opt; show -format png -prefix sub"


# Open waveform
wave: sim
	gtkwave sub.vcd


# Clean generated files
clean-all:
	$(MAKE) clean
	rm -f sub.vcd
	rm -f sub_netlist.v
	rm -f sub.png
	rm -f results.xml
	rm -rf sim_build/


# Cocotb simulation rules
include $(shell cocotb-config --makefiles)/Makefile.sim
