#SIM ?= icarus
#TOPLEVEL_LANG ?= verilog
#
#VERILOG_SOURCES += $(PWD)/gates.v
#TOPLEVEL ?= and_gate
#COCOTB_TEST_MODULES = test_gates
#COCOTB_TESTCASE ?= test_and
#
#include $(shell cocotb-config --makefiles)/Makefile.sim

## Makefile
#TOPLEVEL_LANG = verilog
#SIM ?= icarus
#
#VERILOG_SOURCES = $(PWD)/logic_model.sv
#TOPLEVEL = logic_model
#MODULE = test_logic_model
#
#include $(shell cocotb-config --makefiles)/Makefile.sim

# Makefile for adder
#TOPLEVEL_LANG = verilog
#SIM ?= icarus
#
#VERILOG_SOURCES = $(PWD)/adder.v
#TOPLEVEL = adder
#MODULE = test_adder
#
#include $(shell cocotb-config --makefiles)/Makefile.sim

# Makefile for adder
#TOPLEVEL_LANG = verilog
#SIM ?= icarus
#
#VERILOG_SOURCES = $(PWD)/subs.v
#TOPLEVEL = subs
#MODULE = test_subs
#
#include $(shell cocotb-config --makefiles)/Makefile.sim

# Makefile for adder
TOPLEVEL_LANG = verilog
SIM ?= icarus

VERILOG_SOURCES = $(PWD)/alu.v
TOPLEVEL = alu
MODULE = test_alu

include $(shell cocotb-config --makefiles)/Makefile.sim