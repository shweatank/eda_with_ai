module not_gate (
    input  wire a,
    output wire y
);

    assign y = ~a;

    initial begin
        $dumpfile("dump_not.vcd");
        $dumpvars(0,not_gate);
    end

endmodule