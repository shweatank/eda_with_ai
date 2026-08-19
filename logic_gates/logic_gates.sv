module logic_gates (
    input  wire a,
    input  wire b,
    output wire and_y,
    output wire or_y,
    output wire not_y,
    output wire nand_y,
    output wire nor_y
);
    assign and_y  = a & b;
    assign or_y   = a | b;
    assign not_y  = ~a;
    assign nand_y = ~(a & b);
    assign nor_y  = ~(a | b);

    initial begin
        $dumpfile("logic_gates.vcd");
        $dumpvars(0, logic_gates);
    end
endmodule
