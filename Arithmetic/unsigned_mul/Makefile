SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(CURDIR)/unsigned_mul.sv
TOPLEVEL = unsigned_mul
COCOTB_TEST_MODULES = test_unsigned_mul

COMPILE_ARGS += -g2012
SIM_ARGS += -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim
