SIM ?= icarus

TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES = $(PWD)/decoder_2to4.sv

TOPLEVEL = decoder_2to4

MODULE = testbench_decoder_2to4

COMPILE_ARGS = -g2012

SIM_ARGS = -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim


.PHONY: all run clean


all: run


run:
	$(MAKE) sim


clean::
	rm -rf sim_build
	rm -f *.vcd
	rm -f *.xml
	rm -f *.vvp