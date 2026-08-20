module arith_unit #(
    parameter WIDTH = 8,
    parameter OP = 2
)(
    input  wire signed [WIDTH-1:0] a,
    input  wire signed [WIDTH-1:0] b,
    output reg  signed [(2*WIDTH)-1:0] y
);

    always @(*) begin
        case (OP)   // use parameter, not input
            3'b000: y = a + b;
            3'b001: y = a - b;
            3'b010: y = a * b;
            3'b011: y = (b != 0) ? a / b : 0;
            3'b100: y = (b != 0) ? a % b : 0;
            3'b101: y = a;
            3'b110: y = b;
            3'b111: y = 0;
            default: y = 0;
        endcase
    end
    initial begin
        $dumpfile("arith_unit.vcd");
        $dumpvars(0, arith_unit);
    end

endmodule
