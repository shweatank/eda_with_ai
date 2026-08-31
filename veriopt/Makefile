# Directories
SRC_DIR = src
TB_DIR = tb
RESULTS_DIR = results
SCRIPTS_DIR = scripts
GDS_DIR = gdsii

DESIGN = $(shell ls -t $(SRC_DIR)/*.sv 2>/dev/null | head -n1)
NETLIST = $(RESULTS_DIR)/design_netlist.v
VCD = $(RESULTS_DIR)/design.vcd

all: sim synth profile gds report

sim:
	@echo "▶ Running Cocotb simulation..."
	@mkdir -p $(RESULTS_DIR)
	@if [ -f $(DESIGN) ]; then \
        pytest -v --tb=short $(TB_DIR) || (echo "Simulation failed" && ollama run llama2:7b "Fix simulation errors"); \
    else \
        echo "No RTL design found in $(SRC_DIR). Generate a design first."; \
    fi

synth:
	@echo "⚙ Running Yosys synthesis..."
	@mkdir -p $(RESULTS_DIR)
	@if [ -f $(DESIGN) ]; then \
        yosys -p "read_verilog $(DESIGN); synth; write_verilog $(NETLIST)" || (echo "Synthesis failed" && ollama run llama2:7b "Fix synthesis errors"); \
    else \
        echo "No RTL design found in $(SRC_DIR). Generate a design first."; \
    fi

profile:
	@echo "📊 Running profiling..."
	@if [ -f $(NETLIST) ] && [ -f $(VCD) ]; then \
        python $(SCRIPTS_DIR)/profile.py $(NETLIST) $(VCD) results/sta.rpt || (echo "Profiling failed" && ollama run llama2:7b "Optimize RTL"); \
    else \
        echo "Missing netlist or VCD file. Run simulation and synthesis first."; \
    fi

gds:
	@echo "🏗 Running P&R to GDSII..."
	@mkdir -p $(GDS_DIR)
	@openroad -exit $(SCRIPTS_DIR)/pnr.tcl
	@mv results/design.gds $(GDS_DIR)/design.gds

report:
	@echo "🧠 Generating AI analysis report..."
    @ollama run llama2:7b "Analyze timing, area, power, and DRC/LVS results for design" > $(RESULTS_DIR)/ai_report.txt

wave:
	@echo "🌊 Opening GTKWave..."
	@if [ -f $(VCD) ]; then \
        gtkwave $(VCD); \
    else \
        echo "Waveform file not found. Run simulation first."; \
    fi

clean:
	@echo "🧹 Cleaning results directory..."
	@rm -rf $(RESULTS_DIR)/* $(GDS_DIR)/*
	@echo "🗑 Cleaning database entries..."
	@sqlite3 veriopt.db "DELETE FROM designs;"