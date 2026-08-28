SIM ?= icarus
DATA_WIDTH ?= 8
FIFO_DEPTH ?= 4
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(CURDIR)/apb_uart.sv
TOPLEVEL = apb_uart
COCOTB_TEST_MODULES = test_apb_uart
COMPILE_ARGS += -g2012 -P apb_uart.DATA_WIDTH=$(DATA_WIDTH) -P apb_uart.FIFO_DEPTH=$(FIFO_DEPTH)
SIM_ARGS += -lxt2
include $(shell cocotb-config --makefiles)/Makefile.sim
.PHONY: artifacts clean_apb_uart
artifacts: apb_uart.vcd apb_uart_netlist.v apb_uart.dot apb_uart.png
apb_uart.vcd: apb_uart.sv waveform_tb.sv
	iverilog -g2012 -o apb_uart_waveform.vvp apb_uart.sv waveform_tb.sv
	vvp apb_uart_waveform.vvp
apb_uart_netlist.v: apb_uart.sv
	yosys -p "read_verilog -sv apb_uart.sv; hierarchy -top apb_uart; proc; opt; write_verilog -noattr apb_uart_netlist.v"
apb_uart.dot: apb_uart.sv
	yosys -p "read_verilog -sv apb_uart.sv; hierarchy -top apb_uart; proc; opt; show -format dot -prefix apb_uart"
apb_uart.png: apb_uart.dot
	dot -Tpng apb_uart.dot -o apb_uart.png
clean_apb_uart:
	rm -rf sim_build results.xml *.vcd *.vvp *.dot *.png *_netlist.v
