if {![file exists "libraries/sky130_fd_sc_hd__tt_025C_1v80.lib"]} {
    puts stderr "ERROR: Missing Sky130 Liberty file: libraries/sky130_fd_sc_hd__tt_025C_1v80.lib"
    exit 1
}

read_liberty libraries/sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog build/and_ff_netlist.v
link_design and_ff
read_sdc constraints/and_ff.sdc

report_clock_properties

puts "===================================="
puts "SETUP TIMING"
puts "===================================="
report_checks -path_delay max -fields {slew cap input_pins} -digits 3

puts "===================================="
puts "HOLD TIMING"
puts "===================================="
report_checks -path_delay min -fields {slew cap input_pins} -digits 3

puts "===================================="
puts "END STA"
puts "===================================="
