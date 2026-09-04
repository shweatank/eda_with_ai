// 2:1 Multiplexer (single-bit)
// sel = 0 -> y = a
// sel = 1 -> y = b
module mux2 (
    input  wire a,
    input  wire b,
    input  wire sel,
    output wire y
);
    assign y = sel ? b : a;

    initial begin
        $dumpfile("mux_singlebit.vcd");
        $dumpvars(0, mux2);
    end
endmodule