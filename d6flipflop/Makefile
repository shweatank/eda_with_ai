SIM ?= icarus

TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES := $(CURDIR)/flipflop.sv

TOPLEVEL := dff_1bit

COCOTB_TEST_MODULES := testbench_flipflop

COMPILE_ARGS += -g2012

include $(shell cocotb-config --makefiles)/Makefile.sim


.PHONY: all synth png clean-extra


all: sim synth png


synth:
	yosys -s synth.ys


png: synth
	dot -Tpng dff_synth.dot -o dff_synth.png


clean-extra:
	rm -rf __pycache__
	rm -f dff_waveform.vcd
	rm -f dff_netlist.v
	rm -f dff_synth.dot
	rm -f dff_synth.png
	rm -f results.xml