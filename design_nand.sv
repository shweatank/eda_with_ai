// NAND gate
module nand_gate (
    input  wire a,
    input  wire b,
    output wire y
);
    assign y = ~(a & b);

    initial begin
        $dumpfile("nand_gate.vcd");
        $dumpvars(0, nand_gate);
    end
endmodule

