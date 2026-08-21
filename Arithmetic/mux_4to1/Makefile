SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(PWD)/mux4.sv
VERILOG_SOURCES += $(PWD)/waveform_tb.sv

TOPLEVEL = mux4_tb
COCOTB_TEST_MODULES = test_mux4

COMPILE_ARGS += -g2012
SIM_ARGS += -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim
