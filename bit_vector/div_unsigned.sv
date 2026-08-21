module div_unsigned (
    input  wire [7:0] a,       
    input  wire [7:0] b,       
    output wire [7:0] quotient,
    output wire [7:0] remainder
);
    assign quotient  = a / b;
    assign remainder = a % b;

    initial begin
        $dumpfile("div_unsigned.vcd");
        $dumpvars(0, div_unsigned);
    end
endmodule
