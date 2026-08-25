SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(CURDIR)/rom.sv

TOPLEVEL = rom
COCOTB_TEST_MODULES = test_rom

COMPILE_ARGS += -g2012
SIM_ARGS += -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: artifacts clean_rom
artifacts: rom.vcd rom_netlist.v rom.dot rom.png

rom.vcd: rom.sv waveform_tb.sv
	iverilog -g2012 -o rom_waveform.vvp rom.sv waveform_tb.sv
	vvp rom_waveform.vvp

rom_netlist.v: rom.sv
	yosys -p "read_verilog -sv rom.sv; hierarchy -top rom; proc; opt; write_verilog -noattr rom_netlist.v"

rom.dot: rom.sv
	yosys -p "read_verilog -sv rom.sv; hierarchy -top rom; proc; opt; show -format dot -prefix rom"

rom.png: rom.dot
	dot -Tpng rom.dot -o rom.png

clean_rom:
	rm -rf sim_build results.xml *.vcd *.vvp *.dot *.png *_netlist.v
