TOPLEVEL_LANG = verilog

VERILOG_SOURCES = $(PWD)/counter.sv

TOPLEVEL = counter

COCOTB_TEST_MODULES = testbench_counter

SIM = icarus

COMPILE_ARGS += -g2012

.DEFAULT_GOAL := all

.PHONY: all netlist rtl png clean_all


# Run simulation, synthesis, and PNG generation
all: sim netlist png


# Cocotb configuration
export PYTHONPATH := $(PWD):$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim


# Generate synthesized netlist using Yosys
netlist:
	@echo "=========================================="
	@echo "Generating synthesized netlist..."
	@echo "=========================================="
	yosys -p "read_verilog -sv counter.sv; hierarchy -top counter; proc; opt; write_verilog counter_netlist.v"


# Generate RTL schematic DOT file
rtl:
	@echo "=========================================="
	@echo "Generating RTL schematic..."
	@echo "=========================================="
	yosys -p "read_verilog -sv counter.sv; hierarchy -top counter; proc; opt; show -format dot -prefix counter_rtl"


# Generate PNG schematic
png: rtl
	@echo "=========================================="
	@echo "Generating PNG schematic..."
	@echo "=========================================="
	dot -Tpng counter_rtl.dot -o counter.png


# Clean generated files
clean_all:
	rm -rf sim_build
	rm -f results.xml
	rm -f *.vcd
	rm -f *.vvp
	rm -f *_netlist.v
	rm -f *.dot
	rm -f *.png