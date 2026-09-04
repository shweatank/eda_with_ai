# Simulator Selection (default: icarus)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Design Source File
VERILOG_SOURCES += $(PWD)/signed_unsigned_multiply.sv

# Top-level Module & Python Test Module
# Override when running: make TOPLEVEL=<module> COCOTB_TEST_MODULES=<testbench>
TOPLEVEL ?= multiplier_unsigned
COCOTB_TEST_MODULES ?= testbench_signed_unsigned_multiply

# Give each build its own directory
SIM_BUILD ?= sim_build/$(TOPLEVEL)

# Extra compile/sim arguments
COMPILE_ARGS += -g2012
SIM_ARGS     += -lxt2

# Include cocotb build rules
include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: unsigned signed top all show_unsigned show_signed show_top clean

# Run only the unsigned multiplier test
unsigned:
	$(MAKE) sim TOPLEVEL=multiplier_unsigned COCOTB_TEST_MODULES=testbench_signed_unsigned_multiply SIM_BUILD=sim_build/multiplier_unsigned

# Run only the signed multiplier test
signed:
	$(MAKE) sim TOPLEVEL=multiplier_signed COCOTB_TEST_MODULES=testbench_signed_unsigned_multiply SIM_BUILD=sim_build/multiplier_signed

# Run the combined top module (both multipliers together)
top:
	$(MAKE) sim TOPLEVEL=multiplier_top COCOTB_TEST_MODULES=testbench_signed_unsigned_multiply SIM_BUILD=sim_build/multiplier_top

# Run everything
all:
	$(MAKE) unsigned
	$(MAKE) signed
	$(MAKE) top

# Schematic + netlist for unsigned multiplier
show_unsigned:
	yosys -p "read_verilog -sv signed_unsigned_multiply.sv; synth -top multiplier_unsigned; write_verilog -noattr multiplier_unsigned_netlist.v; show -format png -prefix multiplier_unsigned multiplier_unsigned"

# Schematic + netlist for signed multiplier
show_signed:
	yosys -p "read_verilog -sv signed_unsigned_multiply.sv; synth -top multiplier_signed; write_verilog -noattr multiplier_signed_netlist.v; show -format png -prefix multiplier_signed multiplier_signed"

# Schematic + netlist for combined top module
show_top:
	yosys -p "read_verilog -sv signed_unsigned_multiply.sv; synth -top multiplier_top; write_verilog -noattr multiplier_top_netlist.v; show -format png -prefix multiplier_top multiplier_top"

# Clean build artifacts
clean::
	rm -rf sim_build *.vcd *.xml *.png *.dot *.vvp *_netlist.v