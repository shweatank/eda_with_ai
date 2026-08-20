module adder (
    input  signed [7:0] a,
    input  signed [7:0] b,
    output signed [8:0] y
);
    assign y = a + b;

    initial begin
        $dumpfile("adder_logic.vcd");
        $dumpvars(0, adder);
    end
endmodule

