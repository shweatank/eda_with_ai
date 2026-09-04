# Simulator Selection (default: icarus)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Design Source File
VERILOG_SOURCES += $(PWD)/arithmaticoperations.sv

# Top-level Module & Python Test Module
# Override when running: make TOPLEVEL=<module> COCOTB_TEST_MODULES=<testbench>
TOPLEVEL ?= adder_unsigned
COCOTB_TEST_MODULES ?= testbench_arithmaticoperations

# Give each build its own directory
SIM_BUILD ?= sim_build/$(TOPLEVEL)

# Extra compile/sim arguments
COMPILE_ARGS += -g2012
SIM_ARGS     += -lxt2

# Include cocotb build rules
include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: add_unsigned add_signed sub_unsigned sub_signed mul_unsigned mul_signed \
        div_unsigned div_signed top all \
        show_add_unsigned show_add_signed show_sub_unsigned show_sub_signed \
        show_mul_unsigned show_mul_signed show_div_unsigned show_div_signed show_top \
        clean

# ---------------- Simulation targets ----------------

add_unsigned:
	$(MAKE) sim TOPLEVEL=adder_unsigned COCOTB_TEST_MODULES=testbench_arithmaticoperations SIM_BUILD=sim_build/adder_unsigned

add_signed:
	$(MAKE) sim TOPLEVEL=adder_signed COCOTB_TEST_MODULES=testbench_arithmaticoperations SIM_BUILD=sim_build/adder_signed

sub_unsigned:
	$(MAKE) sim TOPLEVEL=subtractor_unsigned COCOTB_TEST_MODULES=testbench_arithmaticoperations SIM_BUILD=sim_build/subtractor_unsigned

sub_signed:
	$(MAKE) sim TOPLEVEL=subtractor_signed COCOTB_TEST_MODULES=testbench_arithmaticoperations SIM_BUILD=sim_build/subtractor_signed

mul_unsigned:
	$(MAKE) sim TOPLEVEL=multiplier_unsigned COCOTB_TEST_MODULES=testbench_arithmaticoperations SIM_BUILD=sim_build/multiplier_unsigned

mul_signed:
	$(MAKE) sim TOPLEVEL=multiplier_signed COCOTB_TEST_MODULES=testbench_arithmaticoperations SIM_BUILD=sim_build/multiplier_signed

div_unsigned:
	$(MAKE) sim TOPLEVEL=divider_unsigned COCOTB_TEST_MODULES=testbench_arithmaticoperations SIM_BUILD=sim_build/divider_unsigned

div_signed:
	$(MAKE) sim TOPLEVEL=divider_signed COCOTB_TEST_MODULES=testbench_arithmaticoperations SIM_BUILD=sim_build/divider_signed

top:
	$(MAKE) sim TOPLEVEL=alu_top COCOTB_TEST_MODULES=testbench_arithmaticoperations SIM_BUILD=sim_build/alu_top

all:
	$(MAKE) add_unsigned
	$(MAKE) add_signed
	$(MAKE) sub_unsigned
	$(MAKE) sub_signed
	$(MAKE) mul_unsigned
	$(MAKE) mul_signed
	$(MAKE) div_unsigned
	$(MAKE) div_signed
	$(MAKE) top

# ---------------- Schematic + netlist targets ----------------

show_add_unsigned:
	yosys -p "read_verilog -sv arithmaticoperations.sv; synth -top adder_unsigned; write_verilog -noattr adder_unsigned_netlist.v; show -format png -prefix adder_unsigned adder_unsigned"

show_add_signed:
	yosys -p "read_verilog -sv arithmaticoperations.sv; synth -top adder_signed; write_verilog -noattr adder_signed_netlist.v; show -format png -prefix adder_signed adder_signed"

show_sub_unsigned:
	yosys -p "read_verilog -sv arithmaticoperations.sv; synth -top subtractor_unsigned; write_verilog -noattr subtractor_unsigned_netlist.v; show -format png -prefix subtractor_unsigned subtractor_unsigned"

show_sub_signed:
	yosys -p "read_verilog -sv arithmaticoperations.sv; synth -top subtractor_signed; write_verilog -noattr subtractor_signed_netlist.v; show -format png -prefix subtractor_signed subtractor_signed"

show_mul_unsigned:
	yosys -p "read_verilog -sv arithmaticoperations.sv; synth -top multiplier_unsigned; write_verilog -noattr multiplier_unsigned_netlist.v; show -format png -prefix multiplier_unsigned multiplier_unsigned"

show_mul_signed:
	yosys -p "read_verilog -sv arithmaticoperations.sv; synth -top multiplier_signed; write_verilog -noattr multiplier_signed_netlist.v; show -format png -prefix multiplier_signed multiplier_signed"

show_div_unsigned:
	yosys -p "read_verilog -sv arithmaticoperations.sv; synth -top divider_unsigned; write_verilog -noattr divider_unsigned_netlist.v; show -format png -prefix divider_unsigned divider_unsigned"

show_div_signed:
	yosys -p "read_verilog -sv arithmaticoperations.sv; synth -top divider_signed; write_verilog -noattr divider_signed_netlist.v; show -format png -prefix divider_signed divider_signed"

show_top:
	yosys -p "read_verilog -sv arithmaticoperations.sv; synth -top alu_top; write_verilog -noattr alu_top_netlist.v; show -format png -prefix alu_top alu_top"

# ---------------- Clean ----------------

clean::
	rm -rf sim_build *.vcd *.xml *.png *.dot *.vvp *_netlist.v