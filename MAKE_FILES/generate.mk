SIM = icarus

COMPILE_ARGS += -g2012

VERILOG_SOURCES = $(PWD)/../rtl/generate.sv

COCOTB_TOPLEVEL = vector_and
COCOTB_TEST_MODULES = tests.test_generate

WAVES = 1

export PYTHONPATH := $(PWD)/..:$(PYTHONPATH)

SIM_BUILD = sim_build/generate

.PHONY: all synth netlist show-netlist show-circuit wave clean-all

all: sim synth netlist show-circuit


# Yosys synthesis
synth:
	yosys -p "read_verilog -sv ../rtl/generate.sv; hierarchy -top vector_and; proc; opt; techmap; opt; write_verilog -noattr generate_netlist.v"


# Check that netlist was generated
netlist: synth
	@test -f generate_netlist.v
	@echo "SUCCESS: generate_netlist.v generated"


# Display netlist
show-netlist: synth
	cat generate_netlist.v


# Generate circuit diagram
show-circuit:
	yosys -p "read_verilog -sv ../rtl/generate.sv; hierarchy -top vector_and; proc; opt; techmap; opt; show -format png -prefix generate"


# Open waveform
wave: sim
	gtkwave generate.vcd


# Clean generated files
clean-all:
	rm -f generate.vcd
	rm -f generate_netlist.v
	rm -f generate.png
	rm -f results.xml
	rm -rf sim_build/generate


include $(shell cocotb-config --makefiles)/Makefile.sim
