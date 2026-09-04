TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(PWD)/ramreadwrite.sv
TOPLEVEL = ram
COCOTB_TEST_MODULES = testbench_ramreadwrite

SIM = icarus
COMPILE_ARGS += -g2012

.DEFAULT_GOAL := all

.PHONY: all netlist rtl png clean_all

all: sim netlist png

export PYTHONPATH := $(PWD):$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim

netlist:
	yosys -p "read_verilog -sv ramreadwrite.sv; hierarchy -top ram; proc; opt; memory; opt; write_verilog ram_netlist.v"

rtl:
	yosys -p "read_verilog -sv ramreadwrite.sv; hierarchy -top ram; proc; opt; memory; opt; show -format dot -prefix ram_rtl"

png: rtl
	dot -Tpng ram_rtl.dot -o ram.png

clean_all:
	rm -rf sim_build
	rm -f results.xml
	rm -f *.vcd
	rm -f *.vvp
	rm -f *_netlist.v
	rm -f *.dot
	rm -f *.png