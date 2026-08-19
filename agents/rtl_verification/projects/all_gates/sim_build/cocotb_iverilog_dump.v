module cocotb_iverilog_dump();
initial begin
    $dumpfile("sim_build/all_gates.fst");
    $dumpvars(0, all_gates);
end
endmodule
