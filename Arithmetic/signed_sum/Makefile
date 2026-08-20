SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(PWD)/signed_sum.sv

TOPLEVEL = signed_sum
COCOTB_TEST_MODULES = test_signed_sum

COMPILE_ARGS += -g2012
SIM_ARGS += -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim
