PRJ = full_adder
VERILOG_FILES = full_adder.sv

all: clean python_run netlist

python_run:
	python3 run_full_adder.py

compile:
	iverilog -g2012 -o sim.out $(VERILOG_FILES)

simulate:
	vvp sim.out

netlist:
	yosys -p "read_verilog -sv $(VERILOG_FILES); synth -top $(PRJ); write_verilog -noattr synth_netlist.v; show -format png -prefix netlist $(PRJ)"

clean:
	rm -f sim.out full_adder.vcd synth_netlist.v netlist.png netlist.dot
