module multiply_unsigned (
    input  wire [7:0]  a,
    input  wire [7:0]  b,
    output wire [15:0] product
);
    assign product = a * b;

    initial begin
        $dumpfile("multiply_unsigned.vcd");
        $dumpvars(0, multiply_unsigned);
    end
endmodule
