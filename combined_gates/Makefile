SIM ?= icarus
WIDTH ?= 8
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(CURDIR)/combined_gates.sv

TOPLEVEL = combined_gates
COCOTB_TEST_MODULES = test_combined_gates

COMPILE_ARGS += -g2012 -Pcombined_gates.WIDTH=$(WIDTH)
SIM_ARGS += -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: artifacts clean_combined_gates
artifacts: combined_gates.vcd combined_gates_netlist.v combined_gates.dot combined_gates.png

combined_gates.vcd: combined_gates.sv waveform_tb.sv
	iverilog -g2012 -o combined_gates_waveform.vvp combined_gates.sv waveform_tb.sv
	vvp combined_gates_waveform.vvp

combined_gates_netlist.v: combined_gates.sv
	yosys -p "read_verilog -sv combined_gates.sv; hierarchy -top combined_gates; proc; opt; write_verilog -noattr combined_gates_netlist.v"

combined_gates.dot: combined_gates.sv
	yosys -p "read_verilog -sv combined_gates.sv; hierarchy -top combined_gates; proc; opt; show -format dot -prefix combined_gates"

combined_gates.png: combined_gates.dot
	dot -Tpng combined_gates.dot -o combined_gates.png

clean_combined_gates:
	rm -rf sim_build results.xml *.vcd *.vvp *.dot *.png *_netlist.v
