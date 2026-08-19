# Simulator Selection (default: icarus)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Design Source Files
VERILOG_SOURCES += $(PWD)/design_and.sv

# Top-level Module & Python Test Module
TOPLEVEL = and_gate
MODULE   = testbench_and

# Extra compile/sim arguments
COMPILE_ARGS += -g2012
SIM_ARGS     += -lxt2

# Include cocotb build rules
include $(shell cocotb-config --makefiles)/Makefile.sim
