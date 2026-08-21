PRJ = mux4
all: clean run netlist

run:
	python3 run_mux4.py

netlist:
	yosys -p "read_verilog -sv mux4.sv; synth -top $(PRJ); show -format png -prefix netlist $(PRJ)"

clean:
	rm -f sim.out mux4.vcd netlist.png netlist.dot