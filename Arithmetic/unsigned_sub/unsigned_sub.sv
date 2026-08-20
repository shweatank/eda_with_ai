module unsigned_sub (
    input  wire [7:0] a,
    input  wire [7:0] b,
    output wire [7:0] diff
);

    assign diff = a - b;

    initial begin
        $dumpfile("dump_unsigned_sub.vcd");
        $dumpvars(0, unsigned_sub);
    end

endmodule
