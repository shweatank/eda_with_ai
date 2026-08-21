PRJ = logic_gates
VERILOG_FILES = logic_gates.sv

all: clean python_run netlist

python_run:
	python3 run_logic_gates.py

netlist:
	yosys -p "read_verilog $(VERILOG_FILES); synth -top $(PRJ); write_verilog -noattr synth_netlist.v; show -format png -prefix netlist $(PRJ)"

clean:
	rm -f sim.out logic_gates.vcd synth_netlist.v netlist.png netlist.dot