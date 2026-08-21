SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(CURDIR)/arithmetic.sv
TOPLEVEL = arithmetic_all
COCOTB_TEST_MODULES = test_arithmetic

COMPILE_ARGS += -g2012
SIM_ARGS += -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim