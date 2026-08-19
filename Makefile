# Use Icarus Verilog
SIM ?= icarus

# HDL language
TOPLEVEL_LANG ?= verilog

# Design source file
VERILOG_SOURCES += $(PWD)/or.sv

# Top-level module from or.sv
COCOTB_TOPLEVEL = or_gate

# Python test module
COCOTB_TEST_MODULES = test_or

# Generate waveform
WAVES = 1

# Include cocotb simulator rules
include $(shell cocotb-config --makefiles)/Makefile.sim