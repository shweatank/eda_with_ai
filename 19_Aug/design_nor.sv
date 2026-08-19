module nor_gate (
    input  wire a,
    input  wire b,
    output wire y
);

    assign y = ~(a | b);

    initial begin
        $dumpfile("dump_nor.vcd");
        $dumpvars(0,nor_gate);
    end

endmodule