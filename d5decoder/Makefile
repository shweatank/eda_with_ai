SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES = $(PWD)/decoder_2to4.sv
TOPLEVEL = decoder_2to4
MODULE   = testbench_decoder_2to4

COMPILE_ARGS = -g2012
SIM_ARGS     = -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: all run show clean

all: run show

run:
	$(MAKE) sim

show:
	yosys -p "read_verilog -sv decoder_2to4.sv; \
	          synth -top decoder_2to4; \
	          write_verilog -noattr decoder_2to4_netlist.v; \
	          show -format png -prefix decoder_2to4 decoder_2to4"

clean::
	rm -rf sim_build *.vcd *.xml *.png *.dot *.vvp *_netlist.v