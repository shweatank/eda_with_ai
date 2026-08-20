module sub_signed (
    input  wire signed [7:0] a,
    input  wire signed [7:0] b,
    output wire signed [7:0] diff
);
    assign diff = a - b;

    initial begin
        $dumpfile("sub_signed.vcd");
        $dumpvars(0, sub_signed);
    end
endmodule
