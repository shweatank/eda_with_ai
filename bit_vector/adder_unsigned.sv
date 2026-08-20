module adder_unsigned (
    input  wire [7:0] a,
    input  wire [7:0] b,
    output wire [7:0] sum
);
    assign sum = a + b;

    initial begin
        $dumpfile("adder_unsigned.vcd");
        $dumpvars(0, adder_unsigned);
    end
endmodule
