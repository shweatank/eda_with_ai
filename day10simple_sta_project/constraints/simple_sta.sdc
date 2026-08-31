# ============================================================
# SIMPLE STA - TIMING CONSTRAINTS
# ============================================================

# Define 10 ns clock = 100 MHz
create_clock \
    -name core_clk \
    -period 10.000 \
    -waveform {0.000 5.000} \
    [get_ports clk]


# ------------------------------------------------------------
# Clock uncertainty
# ------------------------------------------------------------

# Setup uncertainty
set_clock_uncertainty -setup 0.200 [get_clocks core_clk]

# Hold uncertainty
set_clock_uncertainty -hold 0.100 [get_clocks core_clk]


# ------------------------------------------------------------
# Input timing constraints
# ------------------------------------------------------------

# Maximum input delay
set_input_delay \
    -clock core_clk \
    -max 1.000 \
    [get_ports a]

# Minimum input delay
set_input_delay \
    -clock core_clk \
    -min 0.200 \
    [get_ports a]


# ------------------------------------------------------------
# Output timing constraints
# ------------------------------------------------------------

# Maximum output delay
set_output_delay \
    -clock core_clk \
    -max 1.000 \
    [get_ports y]

# Minimum output delay
set_output_delay \
    -clock core_clk \
    -min 0.200 \
    [get_ports y]


# ------------------------------------------------------------
# Reset timing
# ------------------------------------------------------------

# Reset is excluded from normal functional timing analysis
set_false_path \
    -from [get_ports rst]


# ------------------------------------------------------------
# Input transition assumptions
# ------------------------------------------------------------

set_input_transition 0.100 [get_ports a]

set_input_transition 0.100 [get_ports rst]