# ============================================================
# SIMPLE STA - OPENSTA SCRIPT
# ============================================================

# Read standard-cell timing library
read_liberty lib/cells.lib


# Read synthesized gate-level netlist
read_verilog netlist/simple_sta_netlist.v


# Select and link top-level design
link_design simple_sta


# Read timing constraints
read_sdc constraints/simple_sta.sdc


# ------------------------------------------------------------
# Check timing setup
# ------------------------------------------------------------

check_setup


# ------------------------------------------------------------
# Report units
# ------------------------------------------------------------

report_units


# ------------------------------------------------------------
# Report clocks
# ------------------------------------------------------------

report_clocks


# ------------------------------------------------------------
# Report warnings
# ------------------------------------------------------------

report_warnings


# ============================================================
# SETUP ANALYSIS
# ============================================================

report_checks \
    -path_delay max \
    -format full_clock_expanded \
    -fields {slew cap input_pin net fanout} \
    -digits 3


# ============================================================
# HOLD ANALYSIS
# ============================================================

report_checks \
    -path_delay min \
    -format full_clock_expanded \
    -fields {slew cap input_pin net fanout} \
    -digits 3


# ------------------------------------------------------------
# Worst setup slack
# ------------------------------------------------------------

report_worst_slack -max


# ------------------------------------------------------------
# Worst hold slack
# ------------------------------------------------------------

report_worst_slack -min


# ------------------------------------------------------------
# Find unconstrained paths
# ------------------------------------------------------------

report_checks -unconstrained


exit