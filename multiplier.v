module multiplier (
    input  [7:0] a,
    input  [7:0] b,
    output [15:0] y   // max 255*255=65025, needs 16 bits
);
    assign y = a * b;

    initial begin
        $dumpfile("multiplier.vcd");
        $dumpvars(0, multiplier);
    end
endmodule