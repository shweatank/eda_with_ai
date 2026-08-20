module sub_unsigned (
    input  wire [7:0] a,
    input  wire [7:0] b,
    output wire [7:0] diff
);
    assign diff = a - b;

    initial begin
        $dumpfile("sub_unsigned.vcd");
        $dumpvars(0, sub_unsigned);
    end
endmodule
