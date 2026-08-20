module adder_signed (
    input  wire signed [7:0] a,
    input  wire signed [7:0] b,
    output wire signed [7:0] sum
);
    assign sum = a + b;

    initial begin
        $dumpfile("adder_signed.vcd");
        $dumpvars(0, adder_signed);
    end
endmodule
