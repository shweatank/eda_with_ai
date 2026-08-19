module and_gate (
    input  a,
    input  b,
    output y
);

assign y = a & b;

initial begin
    $dumpfile("dump.vcd");
    $dumpvars(0, and_gate);
end

endmodule