SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(CURDIR)/ram.sv

TOPLEVEL = ram
COCOTB_TEST_MODULES = test_ram

COMPILE_ARGS += -g2012
SIM_ARGS += -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: artifacts clean_ram
artifacts: ram.vcd ram_netlist.v ram.dot ram.png

ram.vcd: ram.sv waveform_tb.sv
	iverilog -g2012 -o ram_waveform.vvp ram.sv waveform_tb.sv
	vvp ram_waveform.vvp

ram_netlist.v: ram.sv
	yosys -p "read_verilog -sv ram.sv; hierarchy -top ram; proc; opt; write_verilog -noattr ram_netlist.v"

ram.dot: ram.sv
	yosys -p "read_verilog -sv ram.sv; hierarchy -top ram; proc; opt; show -format dot -prefix ram"

ram.png: ram.dot
	dot -Tpng ram.dot -o ram.png

clean_ram:
	rm -rf sim_build results.xml *.vcd *.vvp *.dot *.png *_netlist.v
