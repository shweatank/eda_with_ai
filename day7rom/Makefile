TOPLEVEL_LANG = verilog

VERILOG_SOURCES = $(PWD)/rom.sv

TOPLEVEL = rom

COCOTB_TEST_MODULES = testbench_rom

SIM = icarus

COMPILE_ARGS += -g2012

.DEFAULT_GOAL := all

.PHONY: all sim netlist rtl png clean_all


# Run everything
all: sim netlist png


# Cocotb simulation
export PYTHONPATH := $(PWD):$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim


# Generate synthesized netlist
netlist:
	@echo "=========================================="
	@echo "Generating synthesized netlist..."
	@echo "=========================================="
	yosys -p "read_verilog -sv rom.sv; hierarchy -top rom; proc; opt; memory; opt; write_verilog rom_netlist.v"


# Generate RTL schematic
rtl:
	@echo "=========================================="
	@echo "Generating RTL schematic..."
	@echo "=========================================="
	yosys -p "read_verilog -sv rom.sv; hierarchy -top rom; proc; opt; memory; opt; show -format dot -prefix rom_rtl"


# Generate PNG schematic
png: rtl
	@echo "=========================================="
	@echo "Generating PNG schematic..."
	@echo "=========================================="
	dot -Tpng rom_rtl.dot -o rom.png


# Clean generated files
clean_all:
	rm -rf sim_build
	rm -f results.xml
	rm -f *.vcd
	rm -f *.vvp
	rm -f *_netlist.v
	rm -f *.dot
	rm -f *.png