module unsigned_mul (
    input  wire [7:0] a,
    input  wire [7:0] b,
    output wire [15:0] product
);

    assign product = a * b;

    initial begin
        $dumpfile("dump_unsigned_mul.vcd");
        $dumpvars(0, unsigned_mul);
    end

endmodule
