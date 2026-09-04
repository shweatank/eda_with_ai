module xor_gate (
    input  wire a,
    input  wire b,
    output wire y
);
    assign y = a ^ b;

    initial begin
        $dumpfile("xor_gate.vcd");
        $dumpvars(0, xor_gate);
    end
endmodule
