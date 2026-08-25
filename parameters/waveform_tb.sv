`timescale 1ns/1ps

module waveform_tb;
    reg clk = 0;
    reg reset = 0;
    wire [7:0] count;

    counter #(.WIDTH(8)) dut (
        .clk(clk),
        .reset(reset),
        .count(count)
    );

    always #5 clk = ~clk;

    initial begin
        $dumpfile("parameters.vcd");
        $dumpvars(0, waveform_tb);

        reset = 1;
        #12 reset = 0;

        #10;
        #10;
        #10;
        #10;
        #10;
        #10;
        #10;
        #10;
        #10;
        #10;

        $finish;
    end
endmodule
