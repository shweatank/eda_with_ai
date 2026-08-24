module half_adder(
    input  wire [3:0] a,
    input  wire [3:0] b,
    output wire [3:0] sum,
    output wire [3:0] carry
);

    // Bitwise XOR for sum
    assign sum   = a ^ b;

    // Bitwise AND for carry
    assign carry = a & b;

    initial begin
        $dumpfile("half_adder.vcd");
        $dumpvars(0, half_adder);
    end
endmodule
