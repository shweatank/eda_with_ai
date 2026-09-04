# Simulator Selection (default: icarus)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Design Source File
VERILOG_SOURCES += $(PWD)/signed_unsigned_divsion.sv

# Top-level Module & Python Test Module
# Override when running: make TOPLEVEL=<module> COCOTB_TEST_MODULES=<testbench>
TOPLEVEL ?= divider_unsigned
COCOTB_TEST_MODULES ?= testbench_signed_unsigned_divsion

# Give each build its own directory
SIM_BUILD ?= sim_build/$(TOPLEVEL)

# Extra compile/sim arguments
COMPILE_ARGS += -g2012
SIM_ARGS     += -lxt2

# Include cocotb build rules
include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: unsigned signed top all show_unsigned show_signed show_top clean

# Run only the unsigned divider test
unsigned:
	$(MAKE) sim TOPLEVEL=divider_unsigned COCOTB_TEST_MODULES=testbench_signed_unsigned_divsion SIM_BUILD=sim_build/divider_unsigned

# Run only the signed divider test
signed:
	$(MAKE) sim TOPLEVEL=divider_signed COCOTB_TEST_MODULES=testbench_signed_unsigned_divsion SIM_BUILD=sim_build/divider_signed

# Run the combined top module (both dividers together)
top:
	$(MAKE) sim TOPLEVEL=divider_top COCOTB_TEST_MODULES=testbench_signed_unsigned_divsion SIM_BUILD=sim_build/divider_top

# Run everything
all:
	$(MAKE) unsigned
	$(MAKE) signed
	$(MAKE) top

# Schematic + netlist for unsigned divider
show_unsigned:
	yosys -p "read_verilog -sv signed_unsigned_divsion.sv; synth -top divider_unsigned; write_verilog -noattr divider_unsigned_netlist.v; show -format png -prefix divider_unsigned divider_unsigned"

# Schematic + netlist for signed divider
show_signed:
	yosys -p "read_verilog -sv signed_unsigned_divsion.sv; synth -top divider_signed; write_verilog -noattr divider_signed_netlist.v; show -format png -prefix divider_signed divider_signed"

# Schematic + netlist for combined top module
show_top:
	yosys -p "read_verilog -sv signed_unsigned_divsion.sv; synth -top divider_top; write_verilog -noattr divider_top_netlist.v; show -format png -prefix divider_top divider_top"

# Clean build artifacts
clean::
	rm -rf sim_build *.vcd *.xml *.png *.dot *.vvp *_netlist.v