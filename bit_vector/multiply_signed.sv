module multiply_signed (
    input  wire signed [7:0]  a,
    input  wire signed [7:0]  b,
    output wire signed [15:0] product
);
    assign product = a * b;

    initial begin
        $dumpfile("multiply_signed.vcd");
        $dumpvars(0, multiply_signed);
    end
endmodule
