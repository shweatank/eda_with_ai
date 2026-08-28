SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(PWD)/merged_code/design_ALU.sv

TOPLEVEL = all_gates
COCOTB_TEST_MODULES = merged_code.test_alu

COMPILE_ARGS += -g2012
SIM_ARGS += -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim
