read_liberty libraries/sky130_fd_sc_hd__tt_025C_1v80.lib

read_verilog netlist/simple_ram_netlist.v

link_design simple_ram

create_clock -name clk -period 10 [get_ports clk]

report_clock_properties

puts "===================================="
puts "        SETUP TIMING"
puts "===================================="

report_checks -path_delay max -fields {slew cap input_pins} -digits 3

puts "===================================="
puts "        HOLD TIMING"
puts "===================================="

report_checks -path_delay min -fields {slew cap input_pins} -digits 3

puts "===================================="
puts "        END STA"
puts "===================================="