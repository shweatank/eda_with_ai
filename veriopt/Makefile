# The place-and-route recipes pipe OpenROAD through `tee` and rely on
# `set -o pipefail` to notice a failure on the left of the pipe. /bin/sh here
# is dash, which has no pipefail, so a crashed tool would silently look like a
# clean run.
SHELL := /bin/bash

# ---------------------------------------------------------------------------
# Directories
# ---------------------------------------------------------------------------
SRC_DIR      = src
TB_DIR       = tb
RESULTS_DIR  = results
SCRIPTS_DIR  = scripts

# Auto-pick the most recently generated design/testbench unless overridden,
# e.g.  make synth DESIGN=src/controller.sv
DESIGN       ?= $(shell ls -t $(SRC_DIR)/*.sv 2>/dev/null | head -n1)
DESIGN_NAME  := $(basename $(notdir $(DESIGN)))

TESTBENCH_SV  = $(TB_DIR)/test_$(DESIGN_NAME).sv
TESTBENCH_PY  = $(TB_DIR)/test_$(DESIGN_NAME).py

VCD          = $(RESULTS_DIR)/design.vcd
NETLIST      = $(RESULTS_DIR)/netlist.v
WAVE_PNG     = $(RESULTS_DIR)/design.png
SYNTH_INPUT  = $(RESULTS_DIR)/_synth_input.sv
RTL_DOT      = $(RESULTS_DIR)/$(DESIGN_NAME)_rtl.dot
SCHEMATIC_PNG = $(RESULTS_DIR)/$(DESIGN_NAME).png

# ---------------------------------------------------------------------------
# Physical implementation (OpenROAD + Sky130HD)
#
# OpenROAD is not packaged for Ubuntu and this machine has no root, so it
# lives in a user-local prefix installed by scripts/setup_openroad.sh, with a
# launcher on PATH. The PDK is the sky130hd platform bundle from
# OpenROAD-flow-scripts -- tech LEF, merged standard-cell LEF, Liberty, and
# the track/tapcell/PDN/RC tcl fragments that scripts/pnr.tcl sources.
# Point PLATFORM_DIR elsewhere to swap PDKs.
# ---------------------------------------------------------------------------
PLATFORM      ?= sky130hd
PLATFORM_DIR  ?= $(HOME)/opt/orfs/flow/platforms/$(PLATFORM)

TECH_LEF      ?= $(PLATFORM_DIR)/lef/sky130_fd_sc_hd.tlef
SC_LEF        ?= $(PLATFORM_DIR)/lef/sky130_fd_sc_hd_merged.lef
LIB_FILE      ?= $(PLATFORM_DIR)/lib/sky130_fd_sc_hd__tt_025C_1v80.lib

PLACE_SITE    ?= unithd
TAP_CELL_NAME ?= sky130_fd_sc_hd__tapvpwrvgnd_1
CTS_BUF_CELL  ?= sky130_fd_sc_hd__clkbuf_4
DIODE_CELL    ?= sky130_fd_sc_hd__diode_2
TIE_CELL      ?= sky130_fd_sc_hd__conb_1
ABC_DRIVER    ?= sky130_fd_sc_hd__buf_1
FILL_CELLS    ?= sky130_fd_sc_hd__fill_1 sky130_fd_sc_hd__fill_2 sky130_fd_sc_hd__fill_4 sky130_fd_sc_hd__fill_8
IO_PLACER_H   ?= met3
IO_PLACER_V   ?= met2
MIN_ROUTING_LAYER     ?= met1
MIN_CLK_ROUTING_LAYER ?= met3
MAX_ROUTING_LAYER     ?= met5

# The platform excludes these from placement: *probe* cells carry metal on
# every layer and *lpflow* cells belong to multi-power-domain designs, so
# letting the resizer or CTS choose one yields an unroutable layout.
DONT_USE_CELLS ?= sky130_fd_sc_hd__probe_p_8 sky130_fd_sc_hd__probec_p_8 \
                  sky130_fd_sc_hd__lpflow_*

# Implementation knobs -- override on the command line, e.g.
#   make pnr CLK_PERIOD=5 CORE_UTIL=55
CLK_PERIOD    ?= 10.0
CORE_UTIL     ?= 40
PLACE_DENSITY ?= 0.60
CORE_MARGIN   ?= 5.0
MIN_CORE_SIDE ?= 55.0
NPROC         ?= $(shell nproc 2>/dev/null || echo 4)

PNR_DIR        = $(RESULTS_DIR)/pnr
MAPPED_NETLIST = $(PNR_DIR)/$(DESIGN_NAME)_mapped.v
SDC_FILE       = $(PNR_DIR)/$(DESIGN_NAME).sdc
USER_SDC       = constraints/$(DESIGN_NAME).sdc
PNR_LOG        = $(PNR_DIR)/$(DESIGN_NAME)_pnr.log
PNR_SUMMARY    = $(PNR_DIR)/$(DESIGN_NAME)_summary.txt
ROUTED_DEF     = $(PNR_DIR)/$(DESIGN_NAME)_routed.def
LAYOUT_PNG     = $(PNR_DIR)/$(DESIGN_NAME)_layout.png
ROUTE_DRC      = $(PNR_DIR)/$(DESIGN_NAME)_route_drc.rpt
STA_LOG        = $(PNR_DIR)/$(DESIGN_NAME)_sta.rpt
STA_SUMMARY    = $(PNR_DIR)/$(DESIGN_NAME)_sta_summary.txt
SIGNOFF_LOG    = $(PNR_DIR)/$(DESIGN_NAME)_signoff.rpt
SIGNOFF_SUMMARY = $(PNR_DIR)/$(DESIGN_NAME)_signoff_summary.txt

# Environment shared by every OpenROAD/OpenSTA invocation below. Kept in one
# variable so the P&R, STA and signoff recipes cannot drift apart on which
# PDK or which design they are pointed at.
PDK_ENV = DESIGN_NAME="$(DESIGN_NAME)" \
          PLATFORM_DIR="$(PLATFORM_DIR)" \
          PNR_DIR="$(PNR_DIR)" \
          TECH_LEF="$(TECH_LEF)" \
          SC_LEF="$(SC_LEF)" \
          LIB_FILE="$(LIB_FILE)" \
          SDC_FILE="$(SDC_FILE)"

.PHONY: all sim sim-cocotb synth wave rtl schematic clean \
        synth-pdk sdc pnr layout-png sta signoff backend pnr-gui pnr-clean setup-openroad

all: sim synth wave schematic

# ---------------------------------------------------------------------------
# Simulation (SystemVerilog testbench via Icarus Verilog)
# The design's own $dumpfile("<name>.vcd") call determines the VCD filename;
# it lands in the project root since we don't cd, matching backend.py's
# glob.glob("*.vcd") + rename-to-results/design.vcd logic.
# ---------------------------------------------------------------------------
sim:
	@echo "Running simulation for $(DESIGN_NAME)..."
	@mkdir -p $(RESULTS_DIR)
	@if [ -z "$(DESIGN)" ]; then \
	        echo "No RTL design found in $(SRC_DIR). Generate a design first."; exit 1; \
	    elif [ ! -f "$(TESTBENCH_SV)" ]; then \
	        echo "Missing SystemVerilog testbench: $(TESTBENCH_SV)"; exit 1; \
	    elif ! command -v iverilog >/dev/null 2>&1; then \
	        echo "iverilog not found. Install with: sudo apt-get install iverilog"; exit 1; \
	    else \
	        iverilog -g2012 -o $(RESULTS_DIR)/$(DESIGN_NAME).vvp $(DESIGN) $(TESTBENCH_SV) && \
	        vvp $(RESULTS_DIR)/$(DESIGN_NAME).vvp; \
	    fi

# ---------------------------------------------------------------------------
# Simulation (Python/cocotb testbench)
# Requires cocotb + Icarus Verilog installed. VERILOG_SOURCES/TOPLEVEL/MODULE
# are passed straight through to cocotb's own Makefile.
# ---------------------------------------------------------------------------
sim-cocotb:
	@echo "Running cocotb simulation for $(DESIGN_NAME)..."
	@mkdir -p $(RESULTS_DIR)
	@if [ -z "$(DESIGN)" ]; then \
	        echo "No RTL design found in $(SRC_DIR). Generate a design first."; exit 1; \
	    elif [ ! -f "$(TESTBENCH_PY)" ]; then \
	        echo "Missing cocotb testbench: $(TESTBENCH_PY)"; exit 1; \
	    elif ! command -v cocotb-config >/dev/null 2>&1; then \
	        echo "cocotb not found. Install with: pip install cocotb"; exit 1; \
	    fi
	@PYTHONPATH=$(abspath $(TB_DIR)):$$PYTHONPATH \
	    $(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim \
	        SIM=icarus \
	        TOPLEVEL_LANG=verilog \
	        VERILOG_SOURCES=$(abspath $(DESIGN)) \
	        TOPLEVEL=$(DESIGN_NAME) \
	        MODULE=test_$(DESIGN_NAME) \
	        COMPILE_ARGS="-g2012"

# ---------------------------------------------------------------------------
# Synthesis
# The $dumpfile/$dumpvars block is simulation-only and is stripped (via
# scripts/strip_dumpblock.py) before Yosys ever sees the file. Verilator
# lint runs first as a hard gate: if the RTL is structurally broken (e.g.
# conflicting edge-sensitive events on the same signal), fail here with a
# clear message instead of a confusing Yosys error.
# ---------------------------------------------------------------------------
synth:
	@echo "Running Yosys synthesis for $(DESIGN_NAME)..."
	@mkdir -p $(RESULTS_DIR)
	@if [ -z "$(DESIGN)" ]; then \
	        echo "No RTL design found in $(SRC_DIR). Generate a design first."; exit 1; \
	    fi
	@if ! command -v verilator >/dev/null 2>&1; then \
	        echo "verilator not found. Install with: sudo apt-get install verilator"; exit 1; \
	    fi
	@if ! command -v yosys >/dev/null 2>&1; then \
	        echo "yosys not found. Install with: sudo apt-get install yosys"; exit 1; \
	    fi
	@python3 $(SCRIPTS_DIR)/strip_dumpblock.py $(DESIGN) $(SYNTH_INPUT)
	@verilator --lint-only $(SYNTH_INPUT) || (echo "Lint failed: RTL is malformed. Regenerate or hand-fix $(DESIGN) before synthesizing." && exit 1)
	@yosys -p "read_verilog -sv $(SYNTH_INPUT); synth; write_verilog $(NETLIST)"

# ---------------------------------------------------------------------------
# Waveform PNG (rendered from the VCD produced by `make sim`)
#
# gtkwave is cleared of a set of GTK/XDG env vars before running. When this
# Makefile (or the Flask backend that calls it) is launched from VS Code's
# integrated terminal, VS Code's own Snap packaging leaks GTK_PATH,
# GTK_EXE_PREFIX, XDG_DATA_DIRS, etc. into the shell environment. gtkwave
# then tries to load GTK modules/theme engines from VS Code's Snap directory
# instead of the system ones, which crashes with a symbol lookup error
# against a mismatched libpthread. Explicitly unsetting these before the
# gtkwave call avoids that regardless of which terminal invoked `make`.
# ---------------------------------------------------------------------------
GTKWAVE_ENV_CLEAN = env -u GTK_EXE_PREFIX -u GTK_PATH -u GIO_MODULE_DIR \
                        -u GTK_IM_MODULE_FILE -u GDK_PIXBUF_MODULE_FILE \
                        -u XDG_DATA_DIRS -u XDG_DATA_HOME \
                        -u GSETTINGS_SCHEMA_DIR -u LOCPATH

wave:
	@echo "Generating waveform PNG..."
	@if [ ! -f "$(VCD)" ]; then \
	        echo "VCD file not found at $(VCD). Run simulation first."; exit 1; \
	    elif ! command -v gtkwave >/dev/null 2>&1; then \
	        echo "gtkwave not found. Install with: sudo apt-get install gtkwave"; exit 1; \
	    else \
	        $(GTKWAVE_ENV_CLEAN) gtkwave -T -o $(WAVE_PNG) $(VCD); \
	    fi

# ---------------------------------------------------------------------------
# RTL schematic (Graphviz .dot, via Yosys `show`)
# Uses the same dump-block-stripped input as synthesis, so the schematic
# reflects synthesizable structure only, not simulation-only boilerplate.
# ---------------------------------------------------------------------------
rtl:
	@echo "Generating RTL schematic for $(DESIGN_NAME)..."
	@mkdir -p $(RESULTS_DIR)
	@if [ -z "$(DESIGN)" ]; then \
	        echo "No RTL design found in $(SRC_DIR). Generate a design first."; exit 1; \
	    fi
	@if ! command -v yosys >/dev/null 2>&1; then \
	        echo "yosys not found. Install with: sudo apt-get install yosys"; exit 1; \
	    fi
	@python3 $(SCRIPTS_DIR)/strip_dumpblock.py $(DESIGN) $(SYNTH_INPUT)
	@yosys -p "read_verilog -sv $(SYNTH_INPUT); hierarchy -top $(DESIGN_NAME); proc; opt; show -format dot -prefix $(RESULTS_DIR)/$(DESIGN_NAME)_rtl"

# ---------------------------------------------------------------------------
# RTL schematic PNG (renders the .dot produced by `make rtl` via Graphviz)
# ---------------------------------------------------------------------------
schematic: rtl
	@echo "Generating RTL schematic PNG for $(DESIGN_NAME)..."
	@if ! command -v dot >/dev/null 2>&1; then \
	        echo "graphviz 'dot' not found. Install with: sudo apt-get install graphviz"; exit 1; \
	    fi
	@dot -Tpng $(RTL_DOT) -o $(SCHEMATIC_PNG)
	@echo "Schematic written to $(SCHEMATIC_PNG)"

# ---------------------------------------------------------------------------
# Install OpenROAD + the Sky130HD platform into a user-local prefix.
# ---------------------------------------------------------------------------
setup-openroad:
	@bash $(SCRIPTS_DIR)/setup_openroad.sh

# ---------------------------------------------------------------------------
# Technology mapping
#
# `make synth` produces a generic netlist, which is fine for inspection but
# has no physical cells for OpenROAD to place. This target re-synthesizes
# against the PDK Liberty so every gate in the netlist is a real sky130 cell
# with a known footprint, timing and pin geometry.
#
# The extra passes past `synth` matter downstream:
#   dfflibmap  maps generic flops to sky130 flops (abc only handles combinational logic)
#   abc -D     targets the clock period, in ps, so mapping is timing-driven
#   hilomap    replaces literal 1'b1/1'b0 with real tie cells; a bare constant
#              has nothing to place and the router has no pin to connect to
#   setundef   drives don't-cares to a definite value rather than leaving x
#   splitnets  breaks vectors into scalars, matching what the LEF pins expose
# ---------------------------------------------------------------------------
synth-pdk:
	@echo "Mapping $(DESIGN_NAME) to $(PLATFORM) standard cells..."
	@mkdir -p $(PNR_DIR)
	@if [ -z "$(DESIGN)" ]; then \
	        echo "No RTL design found in $(SRC_DIR). Generate a design first."; exit 1; \
	    fi
	@if ! command -v yosys >/dev/null 2>&1; then \
	        echo "yosys not found. Install with: sudo apt-get install yosys"; exit 1; \
	    fi
	@if [ ! -f "$(LIB_FILE)" ]; then \
	        echo "PDK Liberty not found at $(LIB_FILE)."; \
	        echo "Run 'make setup-openroad' to fetch the $(PLATFORM) platform."; exit 1; \
	    fi
	@python3 $(SCRIPTS_DIR)/strip_dumpblock.py $(DESIGN) $(SYNTH_INPUT)
	@yosys -p "read_verilog -sv $(SYNTH_INPUT); \
	           hierarchy -check -top $(DESIGN_NAME); \
	           synth -top $(DESIGN_NAME) -flatten; \
	           dfflibmap -liberty $(LIB_FILE); \
	           abc -liberty $(LIB_FILE) -D $(shell echo '$(CLK_PERIOD) * 1000' | bc -l | cut -d. -f1); \
	           hilomap -hicell $(TIE_CELL) HI -locell $(TIE_CELL) LO; \
	           setundef -zero; \
	           splitnets; \
	           opt_clean -purge; \
	           stat -liberty $(LIB_FILE); \
	           write_verilog -noattr $(MAPPED_NETLIST)" 2>&1 | tee $(PNR_DIR)/$(DESIGN_NAME)_synth.log
	@echo "Mapped netlist: $(MAPPED_NETLIST)"

# ---------------------------------------------------------------------------
# Timing constraints
#
# A hand-written constraints/<design>.sdc always wins. Otherwise one is
# derived from the RTL port list, because a design with no create_clock gives
# CTS nothing to build and produces empty timing reports.
# ---------------------------------------------------------------------------
sdc:
	@mkdir -p $(PNR_DIR)
	@if [ -f "$(USER_SDC)" ]; then \
	        echo "Using hand-written constraints: $(USER_SDC)"; \
	        cp $(USER_SDC) $(SDC_FILE); \
	    else \
	        python3 $(SCRIPTS_DIR)/gen_sdc.py $(DESIGN) $(DESIGN_NAME) $(CLK_PERIOD) $(SDC_FILE); \
	    fi

# ---------------------------------------------------------------------------
# Place and route
#
# Runs scripts/pnr.tcl under OpenROAD: floorplan, pin placement, tapcells,
# PDN, global + detailed placement, CTS, global + detailed routing, fillers,
# then reports and a layout PNG.
#
# QT_QPA_PLATFORM=offscreen: the .deb is a GUI build, so the layout render
# goes through Qt. There is no display when this runs from the Flask backend,
# and without the offscreen platform plugin Qt aborts the whole process.
# ---------------------------------------------------------------------------
pnr: synth-pdk sdc
	@echo "Running OpenROAD place and route for $(DESIGN_NAME) on $(PLATFORM)..."
	@if ! command -v openroad >/dev/null 2>&1; then \
	        echo "openroad not found. Run 'make setup-openroad' first."; exit 1; \
	    fi
	@if [ ! -f "$(TECH_LEF)" ] || [ ! -f "$(SC_LEF)" ]; then \
	        echo "PDK LEF files missing under $(PLATFORM_DIR)."; \
	        echo "Run 'make setup-openroad' to fetch the $(PLATFORM) platform."; exit 1; \
	    fi
	@set -o pipefail; \
	    $(PDK_ENV) \
	    MAPPED_NETLIST="$(MAPPED_NETLIST)" \
	    PLACE_SITE="$(PLACE_SITE)" \
	    CORE_UTIL="$(CORE_UTIL)" \
	    PLACE_DENSITY="$(PLACE_DENSITY)" \
	    CORE_MARGIN="$(CORE_MARGIN)" \
	    MIN_CORE_SIDE="$(MIN_CORE_SIDE)" \
	    TAP_CELL_NAME="$(TAP_CELL_NAME)" \
	    CTS_BUF_CELL="$(CTS_BUF_CELL)" \
	    DIODE_CELL="$(DIODE_CELL)" \
	    FILL_CELLS="$(FILL_CELLS)" \
	    DONT_USE_CELLS="$(DONT_USE_CELLS)" \
	    IO_PLACER_H="$(IO_PLACER_H)" \
	    IO_PLACER_V="$(IO_PLACER_V)" \
	    MIN_ROUTING_LAYER="$(MIN_ROUTING_LAYER)" \
	    MIN_CLK_ROUTING_LAYER="$(MIN_CLK_ROUTING_LAYER)" \
	    MAX_ROUTING_LAYER="$(MAX_ROUTING_LAYER)" \
	    NPROC="$(NPROC)" \
	    QT_QPA_PLATFORM=offscreen \
	    openroad -no_init -exit $(SCRIPTS_DIR)/pnr.tcl 2>&1 | tee $(PNR_LOG)
	@$(MAKE) --no-print-directory layout-png DESIGN=$(DESIGN) || \
	    echo "WARNING: layout PNG not rendered; DEF and reports are still valid."
	@python3 $(SCRIPTS_DIR)/summarize.py pnr $(PNR_LOG) $(PNR_SUMMARY) $(ROUTE_DRC)
	@echo "Routed DEF:  $(ROUTED_DEF)"
	@echo "Layout PNG:  $(LAYOUT_PNG)"

# ---------------------------------------------------------------------------
# Render the routed layout to PNG from the OpenDB database.
#
# Separate from `pnr` because the render goes through Qt, and a Qt failure is
# an abort rather than a catchable error -- keeping it out of the P&R process
# means a headless-rendering problem cannot discard a finished route. `pnr`
# invokes this and tolerates failure; run it by hand to retry a render.
# ---------------------------------------------------------------------------
layout-png:
	@if [ ! -f "$(PNR_DIR)/$(DESIGN_NAME).odb" ]; then \
	        echo "No routed database at $(PNR_DIR)/$(DESIGN_NAME).odb. Run 'make pnr' first."; exit 1; \
	    fi
	@DESIGN_NAME="$(DESIGN_NAME)" PNR_DIR="$(PNR_DIR)" QT_QPA_PLATFORM=offscreen \
	    openroad -no_init -exit $(SCRIPTS_DIR)/layout_png.tcl

# ---------------------------------------------------------------------------
# Open the routed database in the OpenROAD GUI (needs a display; local use
# only, same idea as `make wave` launching gtkwave).
# ---------------------------------------------------------------------------
pnr-gui:
	@if [ ! -f "$(PNR_DIR)/$(DESIGN_NAME).odb" ]; then \
	        echo "No routed database at $(PNR_DIR)/$(DESIGN_NAME).odb. Run 'make pnr' first."; exit 1; \
	    fi
	@openroad -gui -no_init -exit_on_error \
	    -threads $(NPROC) \
	    -command "read_db $(PNR_DIR)/$(DESIGN_NAME).odb" || \
	    openroad -gui -no_init

# ---------------------------------------------------------------------------
# Post-route static timing analysis (signoff timing)
#
# Runs under the standalone OpenSTA binary rather than inside OpenROAD, on the
# routed netlist plus the SPEF that OpenRCX extracted from the real routed
# geometry. That makes it an independent check: the delays come from measured
# parasitics, not from the estimates the placer and router optimize against.
# ---------------------------------------------------------------------------
sta:
	@echo "Running post-route STA for $(DESIGN_NAME)..."
	@if ! command -v sta >/dev/null 2>&1; then \
	        echo "OpenSTA 'sta' not found on PATH."; exit 1; \
	    fi
	@if [ ! -f "$(PNR_DIR)/$(DESIGN_NAME)_sta.v" ]; then \
	        echo "No routed netlist at $(PNR_DIR)/$(DESIGN_NAME)_sta.v. Run 'make pnr' first."; exit 1; \
	    fi
	@set -o pipefail; \
	    $(PDK_ENV) sta -no_init -exit $(SCRIPTS_DIR)/sta.tcl 2>&1 | tee $(STA_LOG)
	@python3 $(SCRIPTS_DIR)/summarize.py sta $(STA_LOG) $(STA_SUMMARY)
	@echo "STA report: $(STA_LOG)"

# ---------------------------------------------------------------------------
# Physical design signoff
#
# Asks whether the layout is buildable rather than whether it is fast:
# placement legality, unrouted nets, routing DRC, antenna risk, power-grid
# connectivity and the Liberty's electrical limits, read back off the routed
# OpenDB database.
# ---------------------------------------------------------------------------
signoff:
	@echo "Running physical signoff checks for $(DESIGN_NAME)..."
	@if ! command -v openroad >/dev/null 2>&1; then \
	        echo "openroad not found. Run 'make setup-openroad' first."; exit 1; \
	    fi
	@if [ ! -f "$(PNR_DIR)/$(DESIGN_NAME).odb" ]; then \
	        echo "No routed database at $(PNR_DIR)/$(DESIGN_NAME).odb. Run 'make pnr' first."; exit 1; \
	    fi
	@set -o pipefail; \
	    $(PDK_ENV) openroad -no_init -exit $(SCRIPTS_DIR)/signoff.tcl 2>&1 | tee $(SIGNOFF_LOG)
	@python3 $(SCRIPTS_DIR)/summarize.py signoff $(SIGNOFF_LOG) $(SIGNOFF_SUMMARY) $(ROUTE_DRC)
	@echo "Signoff report: $(SIGNOFF_LOG)"

# Full physical implementation: map, constrain, place and route, then sign off
# on timing and on the layout.
backend: pnr sta signoff

pnr-clean:
	@echo "Cleaning place-and-route results..."
	@rm -rf $(PNR_DIR)

clean:
	@echo "Cleaning results directory..."
	@rm -rf $(RESULTS_DIR)/*