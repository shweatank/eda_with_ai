module not_gate (
    input  a,
    output y
);

assign y = ~a;

initial begin
    $dumpfile("dump.vcd");
    $dumpvars(0, not_gate);
end

endmodule