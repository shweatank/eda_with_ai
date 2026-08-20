SIM = icarus

COMPILE_ARGS += -g2012

VERILOG_SOURCES = $(PWD)/rtl/divider.sv

TOPLEVEL = divider

MODULE = tests.test_divide

WAVES = 1

.PHONY : all synth netlist show-netlist show-circuit wave clean-all

all: sim synth netlist show-circuit

# Yosys synthesis
synth:
	yosys -p "read_verilog -sv rtl/divider.sv; hierarchy -top divider; proc; opt; techmap; opt; write_verilog -noattr divider_netlist.v"


# Check that netlist was generated
netlist: synth
	@test -f divider_netlist.v
	@echo "SUCCESS: divider_netlist.v generated"


# Display netlist
show-netlist: synth
	cat divider_netlist.v


# Generate circuit diagram
show-circuit:
	yosys -p "read_verilog -sv rtl/divider.sv; hierarchy -top divider; proc; opt; techmap; opt; show -format png -prefix divider"


# Open waveform
wave: sim
	gtkwave divider.vcd


# Clean generated files
clean-all:
	$(MAKE) clean
	rm -f divider.vcd
	rm -f divider_netlist.v
	rm -f divider.png
	rm -f results.xml
	rm -rf sim_build/


# Cocotb simulation rules
include $(shell cocotb-config --makefiles)/Makefile.sim
