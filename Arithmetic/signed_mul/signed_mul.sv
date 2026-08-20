module signed_mul (
    input  wire signed [7:0] a,
    input  wire signed [7:0] b,
    output wire signed [15:0] product
);

    assign product = a * b;

    initial begin
        $dumpfile("dump_signed_mul.vcd");
        $dumpvars(0, signed_mul);
    end

endmodule
