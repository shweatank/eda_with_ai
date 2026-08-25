SIM = icarus

COMPILE_ARGS += -g2012

VERILOG_SOURCES = $(PWD)/rtl/rom.sv

COCOTB_TOPLEVEL = rom

COCOTB_TEST_MODULES = tests.test_rom

WAVES = 1
.PHONY: all synth netlist netlist show-netlist show-circuit wave clean-all
all: sim synth netlist show-circuit


# Yosys synthesis
synth:
	yosys -p "read_verilog -sv rtl/rom.sv; hierarchy -top rom; proc; opt; techmap; opt; write_verilog -noattr rom_netlist.v"


# Check that netlist was generated
netlist: synth
	@test -f rom_netlist.v
	@echo "SUCCESS: rom_netlist.v generated"


# Display netlist
show-netlist: synth
	cat rom_netlist.v


# Generate circuit diagram
show-circuit:
	yosys -p "read_verilog -sv rtl/rom.sv; hierarchy -top rom; proc; opt; techmap; opt; show -format png -prefix rom"


# Open waveform
wave: sim
	gtkwave rom.vcd


# Clean generated files
clean-all:
	$(MAKE) clean
	rm -f rom.vcd
	rm -f rom_netlist.v
	rm -f rom.png
	rm -f results.xml
	rm -rf sim_build/


# Cocotb simulation rules
include $(shell cocotb-config --makefiles)/Makefile.sim
