SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(PWD)/combo_logic.sv

TOPLEVEL = combo_logic
COCOTB_TEST_MODULES = test_combo

COMPILE_ARGS += -g2012

include $(shell cocotb-config --makefiles)/Makefile.sim