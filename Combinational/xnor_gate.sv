module xnor_gate (
    input  logic a,
    input  logic b,
    output logic y
);
    assign y = ~(a ^ b);
    initial begin
        $dumpfile("xnor_gate.vcd");   // name of VCD file
        $dumpvars(0, xnor_gate);      // dump all signals in this module
    end
endmodule
