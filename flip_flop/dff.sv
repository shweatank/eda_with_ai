`timescale 1ns/1ps

module dff_1bit (
    input  wire clk,
    input  wire reset,
    input  wire d,
    output reg  q
);

    // Asynchronous active-high reset
    always @(posedge clk or posedge reset) begin
        if (reset)
            q <= 1'b0;
        else
            q <= d;
    end

`ifndef SYNTHESIS
    initial begin
        $dumpfile("dff_waveform.vcd");
        $dumpvars(0, dff_1bit);
    end
`endif

endmodule