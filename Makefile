TOPLEVEL_LANG = verilog
SIM ?= icarus

# Point to all_designs.v containing your Verilog modules
VERILOG_SOURCES = $(PWD)/all_designs.v

# Set whichever module inside all_designs.v you want to test
TOPLEVEL = dff_1bit

# Name of your Python test file (without .py extension)
MODULE = test_all_designs

# Run only the test functions that match the current TOPLEVEL
#COCOTB_TESTCASE = test_alu_add,test_alu_sub,test_alu_mul,test_alu_div,test_alu_div_by_zero,test_alu_random

COCOTB_TESTCASE=test_dff_1bit
include $(shell cocotb-config --makefiles)/Makefile.sim