all: clean run netlist_dec netlist_mux netlist_cmp

run:
	python3 run_all.py

netlist_dec:
	yosys -p "read_verilog -sv combinational_blocks.sv; synth -top decoder_2to4; show -format png -prefix netlist_dec decoder_2to4"

netlist_mux:
	yosys -p "read_verilog -sv combinational_blocks.sv; synth -top mux_if; show -format png -prefix netlist_mux mux_if"

netlist_cmp:
	yosys -p "read_verilog -sv combinational_blocks.sv; synth -top comparator; show -format png -prefix netlist_cmp comparator"

clean:
	rm -f sim.out combined.vcd netlist_*.png netlist_*.dot
