SIM ?= icarus
WIDTH ?= 8
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(CURDIR)/vector_and.sv

TOPLEVEL = vector_and
COCOTB_TEST_MODULES = test_vector_and

COMPILE_ARGS += -g2012 -Pvector_and.WIDTH=$(WIDTH)
SIM_ARGS += -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: artifacts clean_vector_and
artifacts: vector_and.vcd vector_and_netlist.v vector_and.dot vector_and.png

vector_and.vcd: vector_and.sv waveform_tb.sv
	iverilog -g2012 -o vector_and_waveform.vvp vector_and.sv waveform_tb.sv
	vvp vector_and_waveform.vvp

vector_and_netlist.v: vector_and.sv
	yosys -p "read_verilog -sv vector_and.sv; hierarchy -top vector_and; proc; opt; write_verilog -noattr vector_and_netlist.v"

vector_and.dot: vector_and.sv
	yosys -p "read_verilog -sv vector_and.sv; hierarchy -top vector_and; proc; opt; show -format dot -prefix vector_and"

vector_and.png: vector_and.dot
	dot -Tpng vector_and.dot -o vector_and.png

clean_vector_and:
	rm -rf sim_build results.xml *.vcd *.vvp *.dot *.png *_netlist.v
