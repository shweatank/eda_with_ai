module half_adder (
    input  wire [0:7] a,
    input  wire [0:7] b,
    output wire [0:7] sum
);

    assign sum = a ^ b;
    assign carry = a & b

    initial begin
        $dumpfile("dump_sum.vcd");
        $dumpvars(0,sum_op);
    end

endmodule