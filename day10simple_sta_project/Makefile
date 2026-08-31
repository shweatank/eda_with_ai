# ============================================================
# SIMPLE STATIC TIMING ANALYSIS PROJECT
# ============================================================

YOSYS = yosys
STA   = sta

RTL_DIR         = rtl
SCRIPT_DIR      = scripts
CONSTRAINT_DIR  = constraints
NETLIST_DIR     = netlist
REPORT_DIR      = reports

RTL_FILE         = $(RTL_DIR)/simple_sta.v
SYNTH_SCRIPT     = $(SCRIPT_DIR)/synth.ys
STA_SCRIPT       = $(SCRIPT_DIR)/sta.tcl
SDC_FILE         = $(CONSTRAINT_DIR)/simple_sta.sdc

NETLIST_FILE     = $(NETLIST_DIR)/simple_sta_netlist.v
SYNTH_REPORT     = $(REPORT_DIR)/synthesis.log
STA_REPORT       = $(REPORT_DIR)/sta_report.txt


# ============================================================
# DEFAULT TARGET
# ============================================================

all: synth sta


# ============================================================
# CREATE DIRECTORIES
# ============================================================

dirs:
	mkdir -p $(NETLIST_DIR)
	mkdir -p $(REPORT_DIR)


# ============================================================
# SYNTHESIS
# ============================================================

synth: dirs
	$(YOSYS) -s $(SYNTH_SCRIPT) | tee $(SYNTH_REPORT)


# ============================================================
# STATIC TIMING ANALYSIS
# ============================================================

sta: synth
	$(STA) $(STA_SCRIPT) | tee $(STA_REPORT)


# ============================================================
# VIEW NETLIST
# ============================================================

netlist:
	cat $(NETLIST_FILE)


# ============================================================
# VIEW SYNTHESIS REPORT
# ============================================================

synth_report:
	cat $(SYNTH_REPORT)


# ============================================================
# VIEW STA REPORT
# ============================================================

report:
	cat $(STA_REPORT)


# ============================================================
# CLEAN GENERATED FILES
# ============================================================

clean:
	rm -rf $(NETLIST_DIR)
	rm -rf $(REPORT_DIR)


.PHONY: all dirs synth sta netlist synth_report report clean