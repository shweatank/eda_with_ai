SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(CURDIR)/unsigned_sub.sv
TOPLEVEL = unsigned_sub
COCOTB_TEST_MODULES = test_unsigned_sub

COMPILE_ARGS += -g2012
SIM_ARGS += -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim
