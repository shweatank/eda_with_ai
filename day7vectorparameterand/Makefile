TOPLEVEL_LANG = verilog

VERILOG_SOURCES = $(PWD)/parametervector_and.sv
TOPLEVEL = vector_and
COCOTB_TEST_MODULES = testbench_parametervector_and

SIM = icarus
COMPILE_ARGS += -g2012

.DEFAULT_GOAL := all

.PHONY: all netlist rtl png clean_all

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
	yosys -p "read_verilog -sv parametervector_and.sv; hierarchy -top vector_and; proc; opt; write_verilog parametervector_and_netlist.v"


# Generate RTL schematic
rtl:
	@echo "=========================================="
	@echo "Generating RTL schematic..."
	@echo "=========================================="
	yosys -p "read_verilog -sv parametervector_and.sv; hierarchy -top vector_and; proc; opt; show -format dot -prefix parametervector_and_rtl"


# Generate PNG schematic
png: rtl
	@echo "=========================================="
	@echo "Generating PNG schematic..."
	@echo "=========================================="
	dot -Tpng parametervector_and_rtl.dot -o parametervector_and.png


# Clean generated files
clean_all:
	rm -rf sim_build
	rm -f results.xml
	rm -f *.vcd
	rm -f *.vvp
	rm -f *_netlist.v
	rm -f *.dot
	rm -f *.png
	@echo "All generated files removed"