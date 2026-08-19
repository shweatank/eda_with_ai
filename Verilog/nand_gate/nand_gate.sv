module nand_gate (
    input  a,
    input  b,
    output y
);

assign y = ~(a & b);

initial begin
    $dumpfile("dump.vcd");
    $dumpvars(0, nand_gate);
end

endmodule