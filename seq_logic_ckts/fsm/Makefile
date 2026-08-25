SIM ?= icarus
TOPLEVEL_LANG ?= verilog

export PATH := $(abspath $(CURDIR)/../../.venv/bin):$(PATH)

VERILOG_SOURCES += $(CURDIR)/fsm.sv

TOPLEVEL = controller
COCOTB_TEST_MODULES = test_fsm

COMPILE_ARGS += -g2012
SIM_ARGS += -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: synth waveform artifacts clean-all

synth:
	yosys -s synth.ys

waveform:
	gtkwave fsm_waveform.vcd

artifacts: fsm_waveform.vcd fsm_netlist.v fsm.dot fsm.png

fsm_waveform.vcd: fsm.sv
	iverilog -g2012 -o fsm_waveform.vvp fsm.sv
	vvp fsm_waveform.vvp

fsm_netlist.v: synth.ys fsm.sv
	yosys -s synth.ys

fsm.dot: fsm.sv
	yosys -p "read_verilog -sv fsm.sv; hierarchy -top controller; proc; opt; show -format dot -prefix fsm"

fsm.png: fsm.dot
	dot -Tpng fsm.dot -o fsm.png

clean-all:
	rm -rf sim_build
	rm -rf _pycache_
	rm -f results.xml
	rm -f fsm_waveform.vcd
	rm -f fsm_waveform.vvp
	rm -f fsm_netlist.v
	rm -f fsm.dot
	rm -f fsm.png