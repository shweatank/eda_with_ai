SIM = icarus

COMPILE_ARGS += -g2012

VERILOG_SOURCES = $(PWD)/rtl/4bit_adder.sv

TOPLEVEL = four_bit_adder

MODULE = tests.test_four_bit_adder

WAVES = 1

include $(shell cocotb-config --makefiles)/Makefile.sim
