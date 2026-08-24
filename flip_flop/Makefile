SIM ?= icarus

TOPLEVEL_LANG = verilog
TOPLEVEL = dff_1bit
MODULE = test_dff

VERILOG_SOURCES = $(PWD)/dff.v
SIM_BUILD = $(PWD)/sim_build

COMPILE_ARGS += -g2012
WAVES = 1

include $(shell cocotb-config --makefiles)/Makefile.sim


.PHONY: test synth waveform netlist_sim clean-all


test:
	rm -rf sim_build
	$(MAKE) sim


synth:
	yosys -s synth.ys


netlist_sim: synth
	rm -rf netlist_sim_build
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim \
		SIM=icarus \
		TOPLEVEL_LANG=verilog \
		TOPLEVEL=dff_1bit \
		MODULE=test_dff \
		VERILOG_SOURCES=$(PWD)/dff_netlist.v \
		SIM_BUILD=$(PWD)/netlist_sim_build \
		sim


waveform:
	gtkwave dff_waveform.vcd


clean-all:
	rm -rf sim_build netlist_sim_build
	rm -rf __pycache__
	rm -f results.xml
	rm -f dff_waveform.vcd
	rm -f dff_netlist.v
	rm -f dff_synth.dot
	