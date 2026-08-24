SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES = $(PWD)/../all_gates.sv

COCOTB_TOPLEVEL = and_gate

COCOTB_TEST_MODULES = testbench

include $(shell cocotb-config --makefiles)/Makefile.sim
