// 2:1 Multiplexer
module mux2to1 (
    input  wire a,
    input  wire b,
    input  wire sel,
    output wire y
);
    assign y = sel ? b : a;

`ifdef COCOTB_SIM
    initial begin
        $dumpfile("mux2to1.vcd");
        $dumpvars(0, mux2to1);
    end
`endif

endmodule