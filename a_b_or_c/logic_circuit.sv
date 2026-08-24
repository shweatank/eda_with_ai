module logic_circuit (
    input  A,
    input  B,
    input  C,
    output Y
);

assign Y = (A & B) | C;
initial begin
    $dumpfile("dump.vcd");
    $dumpvars(0, logic_circuit);
end
endmodule