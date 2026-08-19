module not_gate (
    input  wire a,
    output wire y
);
    assign y = ~a;

    initial begin
        $dumpfile("not_gate.vcd");
        $dumpvars(0, not_gate);
    end
endmodule
