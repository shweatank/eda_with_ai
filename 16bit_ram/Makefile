SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(CURDIR)/ram16.sv

TOPLEVEL = simple_ram_16bit
COCOTB_TEST_MODULES = test_ram16

COMPILE_ARGS += -g2012
SIM_ARGS += -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: artifacts clean_ram
artifacts: ram16.vcd ram16_netlist.v ram16.dot ram16.png

ram16.vcd: ram16.sv waveform_tb.sv
	iverilog -g2012 -o ram16_waveform.vvp ram16.sv waveform_tb.sv
	vvp ram16_waveform.vvp

ram16_netlist.v: ram16.sv
	yosys -p "read_verilog -sv ram16.sv; hierarchy -top simple_ram_16bit; proc; opt; write_verilog -noattr ram16_netlist.v"

ram16.dot: ram16.sv
	yosys -p "read_verilog -sv ram16.sv; hierarchy -top simple_ram_16bit; proc; opt; show -format dot -prefix ram16"

ram16.png: ram16.dot
	dot -Tpng ram16.dot -o ram16.png

clean_ram:
	rm -rf sim_build results.xml *.vcd *.vvp *.dot *.png *_netlist.v
