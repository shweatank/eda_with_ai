module combo_gate (
    input  wire a,
    input  wire b,
    input  wire c,
    output wire y
);

    assign y = (a & b)|c;

    initial begin
        $dumpfile("dump_combo.vcd");
        $dumpvars(0,combo_gate);
    end

endmodule