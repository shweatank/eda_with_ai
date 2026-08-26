SIM ?= icarus
TOPLEVEL_LANG = verilog

VERILOG_SOURCES = $(PWD)/counter.sv
TOPLEVEL = counter
MODULE = test_counter

COMPILE_ARGS += -g2012

include $(shell cocotb-config --makefiles)/Makefile.sim
