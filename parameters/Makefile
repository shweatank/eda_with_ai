SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(CURDIR)/parameters.sv

TOPLEVEL = counter
COCOTB_TEST_MODULES = test_parameters

COMPILE_ARGS += -g2012
SIM_ARGS += -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: artifacts clean_parameters
artifacts: parameters.vcd parameters_netlist.v parameters.dot parameters.png

parameters.vcd: parameters.sv waveform_tb.sv
	iverilog -g2012 -o parameters_waveform.vvp parameters.sv waveform_tb.sv
	vvp parameters_waveform.vvp

parameters_netlist.v: parameters.sv
	yosys -p "read_verilog -sv parameters.sv; hierarchy -top counter; proc; opt; write_verilog -noattr parameters_netlist.v"

parameters.dot: parameters.sv
	yosys -p "read_verilog -sv parameters.sv; hierarchy -top counter; proc; opt; show -format dot -prefix parameters"

parameters.png: parameters.dot
	dot -Tpng parameters.dot -o parameters.png

clean_parameters:
	rm -rf sim_build results.xml *.vcd *.vvp *.dot *.png *_netlist.v
