module signed_sub (
    input  wire signed [7:0] a,
    input  wire signed [7:0] b,
    output wire signed [8:0] diff
);

    assign diff = a - b;

    initial begin
        $dumpfile("dump_signed_sub.vcd");
        $dumpvars(0, signed_sub);
    end

endmodule
