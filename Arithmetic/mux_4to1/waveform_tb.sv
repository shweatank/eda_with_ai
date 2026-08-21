module mux4_tb (
    input wire [3:0] d,
    input wire [1:0] sel,
    output wire y
);

    mux4 dut (
        .d(d),
        .sel(sel),
        .y(y)
    );

    initial begin
        $dumpfile("dump_mux4.vcd");
        $dumpvars(0, mux4_tb);
    end

endmodule