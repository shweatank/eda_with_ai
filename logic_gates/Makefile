SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(PWD)/gates.v
TOPLEVEL ?= and_gate
COCOTB_TEST_MODULES = test_gates
COCOTB_TESTCASE ?= test_and

include $(shell cocotb-config --makefiles)/Makefile.sim