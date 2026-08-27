TOPLEVEL_LANG = verilog

# Override on the command line, e.g.:  make DATA_WIDTH=32 ADDR_WIDTH=10
DATA_WIDTH ?= 8
ADDR_WIDTH ?= 8
export DATA_WIDTH
export ADDR_WIDTH

VERILOG_SOURCES = $(PWD)/ram8_16_32.sv
TOPLEVEL = ram8_16_32
COCOTB_TEST_MODULES = testbench_ram8_16_32

SIM = icarus
COMPILE_ARGS += -g2012
COMPILE_ARGS += -P$(TOPLEVEL).DATA_WIDTH=$(DATA_WIDTH)
COMPILE_ARGS += -P$(TOPLEVEL).ADDR_WIDTH=$(ADDR_WIDTH)

.DEFAULT_GOAL := sim

.PHONY: all sim netlist rtl png clean_all test8 test16 test32 test_all

# Run everything for the currently selected width
all: sim netlist png

# Cocotb simulation
export PYTHONPATH := $(PWD):$(PYTHONPATH)
include $(shell cocotb-config --makefiles)/Makefile.sim

# Convenience targets: build + simulate at a specific data width,
# each in its own sim_build dir so results don't clobber each other.
test8:
	$(MAKE) sim DATA_WIDTH=8  ADDR_WIDTH=8  SIM_BUILD=sim_build_w8

test16:
	$(MAKE) sim DATA_WIDTH=16 ADDR_WIDTH=8  SIM_BUILD=sim_build_w16

test32:
	$(MAKE) sim DATA_WIDTH=32 ADDR_WIDTH=8  SIM_BUILD=sim_build_w32

# Run all three widths back to back
test_all: test8 test16 test32

# Generate synthesized netlist (for the currently selected DATA_WIDTH/ADDR_WIDTH)
netlist:
	@echo "=========================================="
	@echo "Generating synthesized netlist (DATA_WIDTH=$(DATA_WIDTH), ADDR_WIDTH=$(ADDR_WIDTH))..."
	@echo "=========================================="
	yosys -p "read_verilog -sv ram8_16_32.sv; chparam -set DATA_WIDTH $(DATA_WIDTH) -set ADDR_WIDTH $(ADDR_WIDTH) ram8_16_32; hierarchy -top ram8_16_32; proc; opt; write_verilog ram8_16_32_netlist.v"

# Generate RTL schematic
rtl:
	@echo "=========================================="
	@echo "Generating RTL schematic..."
	@echo "=========================================="
	yosys -p "read_verilog -sv ram8_16_32.sv; chparam -set DATA_WIDTH $(DATA_WIDTH) -set ADDR_WIDTH $(ADDR_WIDTH) ram8_16_32; hierarchy -top ram8_16_32; proc; opt; show -format dot -prefix ram8_16_32_rtl"

# Generate PNG schematic
png: rtl
	@echo "=========================================="
	@echo "Generating PNG schematic..."
	@echo "=========================================="
	dot -Tpng ram8_16_32_rtl.dot -o ram8_16_32.png

# Clean generated files
clean_all:
	rm -rf sim_build sim_build_w8 sim_build_w16 sim_build_w32 __pycache__
	rm -f results.xml
	rm -f *.vcd
	rm -f *.vvp
	rm -f *_netlist.v
	rm -f *.dot
	rm -f *.png
	@echo "All generated files removed"