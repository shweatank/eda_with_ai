TOPLEVEL_LANG = verilog

VERILOG_SOURCES = $(PWD)/controller.v

TOPLEVEL = controller

MODULE = test_controller

SIM = icarus

COMPILE_ARGS += -g2012


# Default command: make
all: test vcd netlist png

# Run Cocotb test
test:
	$(MAKE) -f Makefile.sim

# Generate VCD
vcd:
	@echo "Generating VCD waveform..."
	iverilog -g2012 -o controller.vvp controller.v
	vvp controller.vvp

# Generate synthesized netlist
netlist:
	@echo "Generating synthesized netlist..."
	yosys -p "read_verilog controller.v; proc; opt; write_verilog controller_netlist.v"

# Generate FSM PNG
png:
	@echo "Generating FSM PNG..."
	dot -Tpng controller.dot -o controller.png

clean_all:
	rm -rf sim_build
	rm -f results.xml
	rm -f controller.vvp
	rm -f controller.vcd
	rm -f controller_netlist.v
	rm -f controller.png

include $(shell cocotb-config --makefiles)/Makefile.sim