module arith_unit #(
    parameter WIDTH = 4
)(
    input  wire signed [WIDTH-1:0] a,
    input  wire signed [WIDTH-1:0] b,
    input  wire [2:0] op,   // <-- OP is now an input
    output reg  signed [(2*WIDTH)-1:0] y
);

    always @(*) begin
        case (op)   // use input, not parameter
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
