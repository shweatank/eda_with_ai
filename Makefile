# Simulator Selection (default: icarus)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Design Source Files (all gates in one file)
VERILOG_SOURCES += $(PWD)/all_gates.sv

# Top-level Module & Python Test Module
TOPLEVEL ?= and_gate
COCOTB_TEST_MODULES ?= testbench_all_gates

# Give each gate its own build directory
SIM_BUILD ?= sim_build/$(TOPLEVEL)

# Extra compile/sim arguments
COMPILE_ARGS += -g2012
SIM_ARGS     += -lxt2

# -----------------------------
# Yosys schematic generation
# -----------------------------

.PHONY: show_all show_each clean all_gates

# Wrapper schematic (all gates together)
show_all:
	yosys -p "read_verilog -sv all_gates.sv; synth -top all_gates; write_verilog -noattr all_gates_netlist.v; show -format png -prefix all_gates all_gates"

# Individual gate schematics
show_each:
	yosys -p "read_verilog -sv all_gates.sv; synth -top and_gate;  write_verilog -noattr and_gate_netlist.v;  show -format png -prefix and_gate and_gate"
	yosys -p "read_verilog -sv all_gates.sv; synth -top nand_gate; write_verilog -noattr nand_gate_netlist.v; show -format png -prefix nand_gate nand_gate"
	yosys -p "read_verilog -sv all_gates.sv; synth -top nor_gate;  write_verilog -noattr nor_gate_netlist.v;  show -format png -prefix nor_gate nor_gate"
	yosys -p "read_verilog -sv all_gates.sv; synth -top not_gate;  write_verilog -noattr not_gate_netlist.v;  show -format png -prefix not_gate not_gate"
	yosys -p "read_verilog -sv all_gates.sv; synth -top or_gate;   write_verilog -noattr or_gate_netlist.v;   show -format png -prefix or_gate or_gate"
	yosys -p "read_verilog -sv all_gates.sv; synth -top xor_gate;  write_verilog -noattr xor_gate_netlist.v;  show -format png -prefix xor_gate xor_gate"

# -----------------------------
# Cocotb simulation build rules
# -----------------------------
include $(shell cocotb-config --makefiles)/Makefile.sim

# Run all gate tests sequentially
all_gates:
	$(MAKE) TOPLEVEL=and_gate  SIM_BUILD=sim_build/and_gate  COCOTB_TEST_MODULES=testbench_all_gates
	$(MAKE) TOPLEVEL=nand_gate SIM_BUILD=sim_build/nand_gate COCOTB_TEST_MODULES=testbench_all_gates
	$(MAKE) TOPLEVEL=nor_gate  SIM_BUILD=sim_build/nor_gate  COCOTB_TEST_MODULES=testbench_all_gates
	$(MAKE) TOPLEVEL=not_gate  SIM_BUILD=sim_build/not_gate  COCOTB_TEST_MODULES=testbench_all_gates
	$(MAKE) TOPLEVEL=or_gate   SIM_BUILD=sim_build/or_gate   COCOTB_TEST_MODULES=testbench_all_gates
	$(MAKE) TOPLEVEL=xor_gate  SIM_BUILD=sim_build/xor_gate  COCOTB_TEST_MODULES=testbench_all_gates

# -----------------------------
# Clean target
# -----------------------------
clean::
	rm -rf sim_build *.vcd *.xml *.png *.dot *.vvp *_netlist.v