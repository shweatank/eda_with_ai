# Simulator Selection (default: icarus)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Design Source File
VERILOG_SOURCES += $(PWD)/signed_unsigned_substact.sv

# Top-level Module & Python Test Module
# Override when running: make TOPLEVEL=<module> COCOTB_TEST_MODULES=<testbench>
TOPLEVEL ?= subtractor_unsigned
COCOTB_TEST_MODULES ?= testbench_signed_unsigned_substact

# Give each build its own directory
SIM_BUILD ?= sim_build/$(TOPLEVEL)

# Extra compile/sim arguments
COMPILE_ARGS += -g2012
SIM_ARGS     += -lxt2

# Include cocotb build rules
include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: unsigned signed top all show_unsigned show_signed show_top clean

# Run only the unsigned subtractor test
unsigned:
	$(MAKE) sim TOPLEVEL=subtractor_unsigned COCOTB_TEST_MODULES=testbench_signed_unsigned_substact SIM_BUILD=sim_build/subtractor_unsigned

# Run only the signed subtractor test
signed:
	$(MAKE) sim TOPLEVEL=subtractor_signed COCOTB_TEST_MODULES=testbench_signed_unsigned_substact SIM_BUILD=sim_build/subtractor_signed

# Run the combined top module (both subtractors together)
top:
	$(MAKE) sim TOPLEVEL=subtractor_top COCOTB_TEST_MODULES=testbench_signed_unsigned_substact SIM_BUILD=sim_build/subtractor_top

# Run everything
all:
	$(MAKE) unsigned
	$(MAKE) signed
	$(MAKE) top

# Schematic + netlist for unsigned subtractor
show_unsigned:
	yosys -p "read_verilog -sv signed_unsigned_substact.sv; synth -top subtractor_unsigned; write_verilog -noattr subtractor_unsigned_netlist.v; show -format png -prefix subtractor_unsigned subtractor_unsigned"

# Schematic + netlist for signed subtractor
show_signed:
	yosys -p "read_verilog -sv signed_unsigned_substact.sv; synth -top subtractor_signed; write_verilog -noattr subtractor_signed_netlist.v; show -format png -prefix subtractor_signed subtractor_signed"

# Schematic + netlist for combined top module
show_top:
	yosys -p "read_verilog -sv signed_unsigned_substact.sv; synth -top subtractor_top; write_verilog -noattr subtractor_top_netlist.v; show -format png -prefix subtractor_top subtractor_top"

# Clean build artifacts
clean::
	rm -rf sim_build *.vcd *.xml *.png *.dot *.vvp *_netlist.v