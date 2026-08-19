TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += or_gate.sv

COCOTB_TOPLEVEL = or_gate

COCOTB_TEST_MODULES = testbench

COMPILE_ARGS += -g2012
SIM_ARGS += -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim
