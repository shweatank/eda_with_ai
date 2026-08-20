module divider (
    input  [7:0] a,       // dividend
    input  [7:0] b,       // divisor
    output [7:0] quotient,
    output [7:0] remainder,
    output reg div_by_zero
);
    assign quotient  = (b == 0) ? 8'd0 : a / b;
    assign remainder = (b == 0) ? 8'd0 : a % b;

    always @(*) begin
        div_by_zero = (b == 0);
    end

    initial begin
        $dumpfile("divider.vcd");
        $dumpvars(0, divider);
    end
endmodule