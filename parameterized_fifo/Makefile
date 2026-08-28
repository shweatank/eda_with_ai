SIM ?= icarus
DATA_WIDTH ?= 8
FIFO_DEPTH ?= 8
export DATA_WIDTH FIFO_DEPTH
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(CURDIR)/fifo.sv
TOPLEVEL = parameterized_fifo
COCOTB_TEST_MODULES = test_fifo
COMPILE_ARGS += -g2012 -Pparameterized_fifo.DATA_WIDTH=$(DATA_WIDTH) -Pparameterized_fifo.FIFO_DEPTH=$(FIFO_DEPTH)
SIM_ARGS += -lxt2

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: artifacts clean_fifo
artifacts: fifo.vcd fifo_netlist.v fifo.dot fifo.png

fifo.vcd: fifo.sv waveform_tb.sv
	iverilog -g2012 -o fifo_waveform.vvp fifo.sv waveform_tb.sv
	vvp fifo_waveform.vvp

fifo_netlist.v: fifo.sv
	yosys -p "read_verilog -sv fifo.sv; hierarchy -top parameterized_fifo; proc; opt; write_verilog -noattr fifo_netlist.v"

fifo.dot: fifo.sv
	yosys -p "read_verilog -sv fifo.sv; hierarchy -top parameterized_fifo; proc; opt; show -format dot -prefix fifo"

fifo.png: fifo.dot
	dot -Tpng fifo.dot -o fifo.png

clean_fifo:
	rm -rf sim_build results.xml *.vcd *.vvp *.dot *.png *_netlist.v
