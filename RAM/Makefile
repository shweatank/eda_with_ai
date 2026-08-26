SIM ?= icarus
TOPLEVEL_LANG = verilog

VERILOG_SOURCES = $(PWD)/simple_ram.sv
TOPLEVEL = simple_ram
MODULE = test_simple_ram

COMPILE_ARGS += -g2012

include $(shell cocotb-config --makefiles)/Makefile.sim
