module half_adder (
    input  wire [0:7] A,
    input  wire [0:7] B,
    output wire [0:7] sum
);

    assign sum = A ^ B;
    assign carry = A & B

    initial begin
        $dumpfile("dump_sum.vcd");
        $dumpvars(0,sum_op);
    end

endmodule