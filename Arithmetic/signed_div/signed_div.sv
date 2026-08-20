module signed_div (
    input  wire signed [7:0] a,
    input  wire signed [7:0] b,
    output wire signed [7:0] quotient,
    output wire signed [7:0] remainder
);

    assign quotient = (b == 8'sd0) ? 8'sd0 : a / b;
    assign remainder = (b == 8'sd0) ? a : a % b;

    initial begin
        $dumpfile("dump_signed_div.vcd");
        $dumpvars(0, signed_div);
    end

endmodule
