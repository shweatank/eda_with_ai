TOPLEVEL_LANG = verilog

VERILOG_SOURCES = $(PWD)/vector_and.sv

TOPLEVEL = vector_and

COCOTB_TEST_MODULES = testbench_vector_and

SIM = icarus

COMPILE_ARGS += -g2012

.DEFAULT_GOAL := all

.PHONY: all vector_and netlist rtl png clean_all

# ==========================================
# RUN EVERYTHING
# ==========================================

all: sim netlist png

# Allow: make vector_and
vector_and: all

# ==========================================
# COCOTB SIMULATION
# ==========================================

export PYTHONPATH := $(PWD):$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim

# ==========================================
# SYNTHESIZED NETLIST
# ==========================================

netlist:
	@echo "=========================================="
	@echo "Generating Synthesized Netlist..."
	@echo "=========================================="
	yosys -p "read_verilog -sv vector_and.sv; hierarchy -top vector_and; proc; opt; techmap; opt; write_verilog vector_and_netlist.v"

# ==========================================
# RTL SCHEMATIC DOT FILE
# ==========================================

rtl:
	@echo "=========================================="
	@echo "Generating RTL Schematic..."
	@echo "=========================================="
	yosys -p "read_verilog -sv vector_and.sv; hierarchy -top vector_and; proc; opt; show -format dot -prefix vector_and_rtl"

# ==========================================
# GENERATE PNG
# ==========================================

png: rtl
	@echo "=========================================="
	@echo "Generating PNG Schematic..."
	@echo "=========================================="
	dot -Tpng vector_and_rtl.dot -o vector_and.png

# ==========================================
# CLEAN GENERATED FILES
# ==========================================

clean_all:
	@echo "Cleaning generated files..."
	rm -rf sim_build
	rm -f results.xml
	rm -f *.vcd
	rm -f *.vvp
	rm -f *_netlist.v
	rm -f *.dot
	rm -f *.png