TOPLEVEL_LANG = verilog

VERILOG_SOURCES = $(PWD)/rtl/and_ff.v
TOPLEVEL = and_ff
COCOTB_TEST_MODULES = test_and_ff
export PYTHONPATH := $(PWD)/tb:$(PYTHONPATH)
SIM = icarus
COMPILE_ARGS += -g2012

include $(shell cocotb-config --makefiles)/Makefile.sim
