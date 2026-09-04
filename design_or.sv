// OR gate
module or_gate (
    input  wire a,
    input  wire b,
    output wire y
);
    assign y = a | b;

    initial begin
        $dumpfile("or_gate.vcd");
        $dumpvars(0, or_gate);
    end
endmodule

