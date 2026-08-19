    // AND gate
    module and_gate (
        input  wire a,
        input  wire b,
        output wire y
    );
        assign y = a & b;

        initial begin
            $dumpfile("and_gate.vcd");
            $dumpvars(0, and_gate);
        end
    endmodule

