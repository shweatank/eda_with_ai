module mux2 (
    input  wire a,
    input  wire b,
    input  wire sel,
    output wire y
);
    assign y = sel ? b : a;

    initial begin
        $dumpfile("mux2.vcd");
        $dumpvars(0, mux2);
    end
endmodule
