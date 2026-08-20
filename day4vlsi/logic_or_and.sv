// Logic: y = (A & B) | C
module logic_or_and (
    input  wire A,
    input  wire B,
    input  wire C,
    output wire y
);
    assign y = (A & B) | C;
    initial begin
        $dumpfile("logic_or_and.vcd");
        $dumpvars(0, logic_or_and);
    end
endmodule
