SIM = icarus

COMPILE_ARGS += -g2012

VERILOG_SOURCES = $(PWD)/rtl/mul.sv

TOPLEVEL =multiplier

MODULE = tests.test_mul

WAVES = 1

.PHONY : all synth netlist show-netlist show-circuit wave clean-all

all: sim synth netlist show-circuit

# Yosys synthesis
synth:
	yosys -p "read_verilog -sv rtl/mul.sv; hierarchy -top muliplier; proc; opt; techmap; opt; write_verilog -noattr muliplier_netlist.v"


# Check that netlist was generated
netlist: synth
	@test -f divider_netlist.v
	@echo "SUCCESS: muliplier_netlist.v generated"


# Display netlist
show-netlist: synth
	cat muliplier_netlist.v


# Generate circuit diagram
show-circuit:
	yosys -p "read_verilog -sv rtl/mul.sv; hierarchy -top muliplier; proc; opt; techmap; opt; show -format png -prefix muliplier"


# Open waveform
wave: sim
	gtkwave multiplier.vcd


# Clean generated files
clean-all:
	$(MAKE) clean
	rm -f multiplier.vcd
	rm -f multiplier_netlist.v
	rm -f multiplier.png
	rm -f results.xml
	rm -rf sim_build/


# Cocotb simulation rules
include $(shell cocotb-config --makefiles)/Makefile.sim
