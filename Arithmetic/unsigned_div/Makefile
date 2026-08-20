SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(CURDIR)/unsigned_div.sv
TOPLEVEL = unsigned_div
COCOTB_TEST_MODULES = test_unsigned_div

COMPILE_ARGS += -g2012
SIM_ARGS += -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim
