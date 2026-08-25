# ============================================================
# SIMPLE RAM EDA + STA FLOW
# ============================================================

TOPLEVEL = simple_ram
SIM = icarus

VERILOG = simple_ram.sv
TESTBENCH = test_simple_ram

NETLIST_DIR = netlist
WAVE_DIR = waves
CONSTRAINT_DIR = constraints
SCRIPT_DIR = scripts
LIB_DIR = libraries
BUILD_DIR = build


# ============================================================
# DEFAULT FLOW
# ============================================================

all: sim synth image sta

	@echo ""
	@echo "===================================="
	@echo " RAM EDA + STA FLOW COMPLETED"
	@echo "===================================="


# ============================================================
# RTL SIMULATION
# ============================================================

sim:
	@echo "===================================="
	@echo " RTL SIMULATION"
	@echo "===================================="

	mkdir -p $(WAVE_DIR)

	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim \
		SIM=$(SIM) \
		TOPLEVEL_LANG=verilog \
		TOPLEVEL=$(TOPLEVEL) \
		MODULE=$(TESTBENCH) \
		VERILOG_SOURCES=$(PWD)/$(VERILOG) \
		COMPILE_ARGS="-g2012 -DCOCOTB_SIM"

	@echo ""
	@echo "RTL SIMULATION PASSED."


# ============================================================
# YOSYS SYNTHESIS
# ============================================================

synth:
	@echo "===================================="
	@echo " YOSYS SYNTHESIS"
	@echo "===================================="

	mkdir -p $(NETLIST_DIR)

	yosys -s simple_ram.ys \
		2>&1 | tee $(NETLIST_DIR)/synthesis_report.txt

	@test -f $(NETLIST_DIR)/simple_ram_netlist.v

	@echo ""
	@echo "SYNTHESIS PASSED."


# ============================================================
# SCHEMATIC GENERATION
# ============================================================

image:
	@echo "===================================="
	@echo " SCHEMATIC GENERATION"
	@echo "===================================="

	mkdir -p $(NETLIST_DIR)

	yosys -p \
		"read_verilog -sv $(VERILOG); hierarchy -top $(TOPLEVEL); proc; opt; show -format svg -prefix $(NETLIST_DIR)/rtl"

	@test -f $(NETLIST_DIR)/simple_ram_netlist.v

	yosys -p \
		"read_verilog $(NETLIST_DIR)/simple_ram_netlist.v; hierarchy -top $(TOPLEVEL); show -format svg -prefix $(NETLIST_DIR)/netlist"

	@echo ""
	@echo "SCHEMATICS GENERATED."


# ============================================================
# STATIC TIMING ANALYSIS
# ============================================================

sta:
	@echo "===================================="
	@echo " STATIC TIMING ANALYSIS"
	@echo "===================================="

	mkdir -p $(BUILD_DIR)

	sta -exit $(SCRIPT_DIR)/sta.tcl \
		2>&1 | tee $(BUILD_DIR)/sta_report.txt

	@echo ""
	@echo "STA COMPLETED."


# ============================================================
# GTKWave
# ============================================================

wave:
	gtkwave $(WAVE_DIR)/rtl.vcd


# ============================================================
# YOSYS STATISTICS
# ============================================================

stat:
	yosys -p \
		"read_verilog -sv $(VERILOG); hierarchy -top $(TOPLEVEL); proc; opt; stat"


# ============================================================
# CLEAN
# ============================================================

clean:
	rm -rf sim_build
	rm -rf $(NETLIST_DIR)
	rm -rf $(WAVE_DIR)
	rm -rf $(BUILD_DIR)
	rm -rf __pycache__
	rm -f results.xml
	rm -f *.vvp
	rm -f *.png

	@echo "Clean completed."