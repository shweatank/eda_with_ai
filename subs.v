module subtractor (
    input  [7:0] a,
    input  [7:0] b,
    output [8:0] y   // 9 bits to hold sign info for a-b (as signed result via MSB)
);
    assign y = a - b;

    initial begin
        $dumpfile("subtractor.vcd");
        $dumpvars(0, subtractor);
    end
endmodule