module cocotb_iverilog_dump();
initial begin
    $dumpfile("sim_build/or_gate.fst");
    $dumpvars(0, or_gate);
end
endmodule
