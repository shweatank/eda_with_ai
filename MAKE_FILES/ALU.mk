SIM = icarus

COMPILE_ARGS += -g2012

VERILOG_SOURCES = $(PWD)/rtl/four_bitALU.sv

TOPLEVEL = four_bit_ALU

MODULE = tests.test_four_ALU

WAVES = 1

include $(shell cocotb-config --makefiles)/Makefile.sim
