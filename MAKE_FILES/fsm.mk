TOPLEVEL_LANG = verilog

VERILOG_SOURCES = $(PWD)/../rtl/fsm.sv

TOPLEVEL = controller

MODULE = fsm

export PYTHONPATH := $(PWD)/../tests

SIM = icarus

COMPILE_ARGS += -g2012

WAVES =1

include $(shell cocotb-config --makefiles)/Makefile.sim
