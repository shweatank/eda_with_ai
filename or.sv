module or_gate (
    input wire a,
    input wire b,
    output wire y
);

    assign y = a | b;

    initial begin 
    $dumpfile("dump_or.vcd");
    $dumpvars(0,or_gate);
    
    end

endmodule