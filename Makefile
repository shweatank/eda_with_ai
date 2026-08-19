SIM ?= iverilog

RTL = rtl/gates.sv

.PHONY: and or not nand nor clean

and:
	TOPLEVEL=and_gate \
	MODULE=test_and \
	make -f $(shell cocotb-config --makefiles)/Makefile.sim \
	SIM=$(SIM) \
	VERILOG_SOURCES=VERILOG_SOURCES = $(PWD)/rtl/basic_gates.sv
	TOPLEVEL=and_gate \
	MODULE=test_and

or:
	TOPLEVEL=or_gate \
	MODULE=test_or \
	make -f $(shell cocotb-config --makefiles)/Makefile.sim \
	SIM=$(SIM) \
	VERILOG_SOURCES=VERILOG_SOURCES = $(PWD)/rtl/basic_gates.sv
	TOPLEVEL=or_gate \
	MODULE=test_or
