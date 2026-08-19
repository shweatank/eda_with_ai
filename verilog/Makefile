# Makefile

TOPLEVEL_LANG = verilog
SIM ?= icarus

# Default to and_gate if no gate is specified
GATE ?= and_gate

VERILOG_SOURCES = $(PWD)/$(GATE).sv

TOPLEVEL = $(GATE)
MODULE = $(GATE)

include $(shell cocotb-config --makefiles)/Makefile.sim
