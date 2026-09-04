TOPLEVEL_LANG = verilog

VERILOG_SOURCES = $(PWD)/parameter_combinedgate.sv
TOPLEVEL = vector_gates_combined
COCOTB_TEST_MODULES = testbench_parameter_combinedgate

SIM = icarus
COMPILE_ARGS += -g2012

.DEFAULT_GOAL := alls

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
	yosys -p "read_verilog -sv parameter_combinedgate.sv; hierarchy -top vector_gates_combined; proc; opt; write_verilog vector_gates_combined_netlist.v"

# Generate RTL schematic
rtl:
	@echo "=========================================="
	@echo "Generating RTL schematic..."
	@echo "=========================================="
	yosys -p "read_verilog -sv parameter_combinedgate.sv; hierarchy -top vector_gates_combined; proc; opt; show -format dot -prefix vector_gates_combined_rtl"

# Generate PNG schematic
png: rtl
	@echo "=========================================="
	@echo "Generating PNG schematic..."
	@echo "=========================================="
	dot -Tpng vector_gates_combined_rtl.dot -o vector_gates_combined.png

# Clean generated files
clean_all:
	rm -rf sim_build __pycache__
	rm -f results.xml
	rm -f *.vcd
	rm -f *.vvp
	rm -f *_netlist.v
	rm -f *.dot
	rm -f *.png
	@echo "All generated files removed"