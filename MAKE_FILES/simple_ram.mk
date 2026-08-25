SIM = icarus

COMPILE_ARGS += -g2012

VERILOG_SOURCES = $(PWD)/rtl/simple_ram.sv

TOPLEVEL = simple_ram

export PYTHONPATH := $(PWD)/tests:$(PYTHONPATH)
MODULE = test_simple_ram

# Put cocotb/Icarus build files here
SIM_BUILD = simbuild/simple_ram

WAVES = 1

.PHONY : all synth netlist show-netlist show-circuit wave clean-all

all: sim synth netlist show-circuit

# Yosys synthesis
synth:
	yosys -p "read_verilog -sv rtl/simple_ram.sv; hierarchy -top simple_ram; proc; opt; techmap; opt; write_verilog -noattr simple_ram_netlist.v"


# Check that netlist was generated
netlist: synth
	@test -f simple_ram_netlist.v
	@echo "SUCCESS: simple_ram_netlist.v generated"


# Display netlist
show-netlist: synth
	cat simple_ram_netlist.v


# Generate circuit diagram
show-circuit:
	yosys -p "read_verilog -sv rtl/simple_ram.sv; hierarchy -top simple_ram; proc; opt; techmap; opt; show -format png -prefix simple_ram"


# Open waveform
wave: sim
	gtkwave simple_ram.vcd


# Clean generated files
clean-all:
	$(MAKE) clean
	rm -f simple_ram.vcd
	rm -f simple_ram_netlist.v
	rm -f simple_ram.png
	rm -f results.xml
	rm -rf sim_build/simple_ram


# Cocotb simulation rules
include $(shell cocotb-config --makefiles)/Makefile.sim
