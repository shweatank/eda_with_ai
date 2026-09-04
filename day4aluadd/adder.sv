// 8-bit adder: y = A + B
module adder (
    input  wire [7:0] A,
    input  wire [7:0] B,
    output wire [7:0] y
);
    assign y = A + B;
    initial begin
        $dumpfile("adder.vcd");
        $dumpvars(0, adder);
    end
endmodule