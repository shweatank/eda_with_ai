SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Ensure the workspace-local cocotb installation is on PATH even without an activated shell.
export PATH := $(abspath $(CURDIR)/../../.venv/bin):$(PATH)

VERILOG_SOURCES += $(CURDIR)/dflipflop.sv
TOPLEVEL = dff_1bit
COCOTB_TEST_MODULES = test_dflipflop

COMPILE_ARGS += -g2012
SIM_ARGS += -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: synth waveform artifacts clean-all

synth:
	yosys -s synth.ys

waveform:
	gtkwave dff_waveform.vcd

artifacts: dff_waveform.vcd dflipflop_netlist.v dff_design.dot dff_design.png

dff_waveform.vcd: dflipflop.sv
	iverilog -g2012 -o dff_waveform.vvp dflipflop.sv
	vvp dff_waveform.vvp

dflipflop_netlist.v: synth.ys dflipflop.sv
	yosys -s synth.ys

dff_design.dot: dflipflop.sv
	yosys -p "read_verilog -sv dflipflop.sv; hierarchy -top dff_1bit; proc; opt; show -format dot -prefix dff_design"

dff_design.png: dff_design.dot
	dot -Tpng dff_design.dot -o dff_design.png

clean-all:
	rm -rf sim_build
	rm -rf _pycache_
	rm -f results.xml
	rm -f dff_waveform.vcd
	rm -f dff_waveform.vvp
	rm -f dff_design.dot
	rm -f dff_design.png
	rm -f dflipflop_netlist.v
	rm -f dflipflop_synth.dot