module div_signed (
    input  wire signed [7:0] a,       // dividend
    input  wire signed [7:0] b,       // divisor
    output wire signed [7:0] quotient,
    output wire signed [7:0] remainder
);
    assign quotient  = a / b;
    assign remainder = a % b;

    initial begin
        $dumpfile("div_signed.vcd");
        $dumpvars(0, div_signed);
    end
endmodule
