module half_adder (
    input  wire a,
    input  wire b,
    output wire sum,
    output wire carry
);
    assign sum   = a ^ b;
    assign carry = a & b;

    initial begin
        $dumpfile("half_adder.vcd");
        $dumpvars(0, half_adder);
    end
endmodule
