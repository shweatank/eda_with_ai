SIM ?= icarus

TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES = $(PWD)/decoder_2to4.sv

TOPLEVEL = decoder_2to4

MODULE = testbench_decoder_2to4

COMPILE_ARGS = -g2012

SIM_ARGS = -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim


.PHONY: all run netlist png show clean


all: run netlist png


# -----------------------------
# Run Cocotb Simulation
# -----------------------------

run:
	$(MAKE) sim


# -----------------------------
# Generate Synthesized Netlist
# -----------------------------

netlist:
	yosys -p "read_verilog -sv decoder_2to4.sv; \
	synth -top decoder_2to4; \
	write_verilog -noattr decoder_2to4_netlist.v"


# -----------------------------
# Generate PNG Schematic
# -----------------------------

png:
	yosys -p "read_verilog -sv decoder_2to4.sv; \
	synth -top decoder_2to4; \
	show -format png -prefix decoder_2to4"


# Alias
show: png


# -----------------------------
# Clean Generated Files
# -----------------------------

clean:
	rm -rf sim_build
	rm -f *.vcd
	rm -f *.xml
	rm -f *.vvp
	rm -f *_netlist.v
	rm -f *.png
	rm -f *.dot