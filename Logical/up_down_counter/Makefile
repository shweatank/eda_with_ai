SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(PWD)/up_down_counter.sv

TOPLEVEL = up_down_counter
COCOTB_TEST_MODULES = test_up_down_counter

COMPILE_ARGS += -g2012
SIM_ARGS += -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: artifacts
artifacts: up_down_counter.vcd up_down_counter_netlist.v up_down_counter.dot up_down_counter.png

up_down_counter.vcd: up_down_counter.sv waveform_tb.sv
	iverilog -g2012 -o up_down_counter_waveform.vvp up_down_counter.sv waveform_tb.sv
	vvp up_down_counter_waveform.vvp

up_down_counter_netlist.v: up_down_counter.sv
	yosys -p "read_verilog -sv up_down_counter.sv; hierarchy -top up_down_counter; proc; opt; write_verilog -noattr up_down_counter_netlist.v"

up_down_counter.dot: up_down_counter.sv
	yosys -p "read_verilog -sv up_down_counter.sv; hierarchy -top up_down_counter; proc; opt; show -format dot -prefix up_down_counter"

up_down_counter.png: up_down_counter.dot
	dot -Tpng up_down_counter.dot -o up_down_counter.png
