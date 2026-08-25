# ============================================================
# PARAMETERIZED COUNTER EDA FLOW
# ============================================================

TOPLEVEL = counter
SIM = icarus

VERILOG = counter.sv
TESTBENCH = test_counter

NETLIST_DIR = netlist
WAVE_DIR = waves


# ============================================================
# DEFAULT FLOW
# ============================================================

all: sim synth image

	@echo ""
	@echo "===================================="
	@echo " COUNTER EDA FLOW COMPLETED"
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

	yosys -s counter.ys \
		2>&1 | tee $(NETLIST_DIR)/synthesis_report.txt

	@test -f $(NETLIST_DIR)/counter_netlist.v

	@echo ""
	@echo "SYNTHESIS PASSED."
	@echo "Netlist:"
	@echo "  $(NETLIST_DIR)/counter_netlist.v"


# ============================================================
# SCHEMATIC GENERATION
# ============================================================

image:
	@echo "===================================="
	@echo " SCHEMATIC GENERATION"
	@echo "===================================="

	mkdir -p $(NETLIST_DIR)

	@echo "Generating RTL schematic..."

	yosys -p \
		"read_verilog -sv $(VERILOG); hierarchy -top $(TOPLEVEL); proc; opt; show -format svg -prefix $(NETLIST_DIR)/rtl"

	@echo "Generating netlist schematic..."

	@test -f $(NETLIST_DIR)/counter_netlist.v

	yosys -p \
		"read_verilog $(NETLIST_DIR)/counter_netlist.v; hierarchy -top $(TOPLEVEL); show -format svg -prefix $(NETLIST_DIR)/netlist"

	@echo ""
	@echo "Images generated:"
	@echo "  $(NETLIST_DIR)/rtl.svg"
	@echo "  $(NETLIST_DIR)/netlist.svg"


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
	rm -rf __pycache__
	rm -f results.xml
	rm -f *.vvp
	rm -f *.png

	@echo "Clean completed."