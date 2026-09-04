TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(PWD)/ram.sv
TOPLEVEL = simple_ram
COCOTB_TEST_MODULES = testbench_simpleram

SIM = icarus
COMPILE_ARGS += -g2012

.DEFAULT_GOAL := all

.PHONY: all sim netlist rtl png clean_all

# Run everything
all: sim netlist png

# Cocotb simulation
include $(shell cocotb-config --makefiles)/Makefile.sim

# Generate synthesized netlist (requires yosys)
netlist:
	@echo "=========================================="
	@echo "Generating synthesized netlist..."
	@echo "=========================================="
	yosys -p "read_verilog -sv ram.sv; hierarchy -top simple_ram; proc; opt; memory; opt; write_verilog simple_ram_netlist.v"

# Generate RTL schematic (requires yosys)
rtl:
	@echo "=========================================="
	@echo "Generating RTL schematic..."
	@echo "=========================================="
	yosys -p "read_verilog -sv ram.sv; hierarchy -top simple_ram; proc; opt; memory; opt; show -format dot -prefix simple_ram_rtl"

# Generate PNG schematic (requires graphviz)
png: rtl
	@echo "=========================================="
	@echo "Generating PNG schematic..."
	@echo "=========================================="
	dot -Tpng simple_ram_rtl.dot -o simple_ram.png

# Clean generated files
clean_all:
	rm -rf sim_build
	rm -f results.xml
	rm -f *.vcd
	rm -f *.vvp
	rm -f *_netlist.v
	rm -f *.dot
	rm -f *.png



module simple_ram (
    input  wire        clk,
    input  wire        write_enable,
    input  wire [7:0]  address,
    input  wire [15:0] write_data,
    output reg  [15:0] read_data
);

    reg [15:0] memory [0:255];

    initial begin
        $dumpfile("simple_ram.vcd");
        $dumpvars(0, simple_ram);
    end

    always @(posedge clk) begin
        if (write_enable)
            memory[address] <= write_data;
        read_data <= memory[address];
    end

endmodule