// 8-bit signed adder: y = A + B (two's complement)
module adder_signed (
    input  wire signed [7:0] A,
    input  wire signed [7:0] B,
    output wire signed [7:0] y
);
    assign y = A + B;
    initial begin
        $dumpfile("adder_signed.vcd");
        $dumpvars(0, adder_signed);
    end
endmodule