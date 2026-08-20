module signed_sum (
    input  wire signed [7:0] a,
    input  wire signed [7:0] b,
    output wire signed [8:0] sum
);

    assign sum = a + b;

    initial begin
        $dumpfile("dump_signed_sum.vcd");
        $dumpvars(0, signed_sum);
    end

endmodule