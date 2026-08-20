module unsigned_div (
    input  wire [7:0] a,
    input  wire [7:0] b,
    output wire [7:0] quotient,
    output wire [7:0] remainder
);

    assign quotient = (b == 8'd0) ? 8'd0 : a / b;
    assign remainder = (b == 8'd0) ? a : a % b;

    initial begin
        $dumpfile("dump_unsigned_div.vcd");
        $dumpvars(0, unsigned_div);
    end

endmodule
