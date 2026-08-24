`timescale 1ns/1ps

module waveform_tb;
    reg clk = 0;
    reg reset = 1;
    reg up = 1;
    wire [7:0] count;

    up_down_counter dut (
        .clk(clk),
        .reset(reset),
        .up(up),
        .count(count)
    );

    always #5 clk = ~clk;

    initial begin
        $dumpfile("up_down_counter.vcd");
        $dumpvars(0, waveform_tb);
        #12 reset = 0;
        #30 up = 0;
        #30 up = 1;
        #20 reset = 1;
        #8 $finish;
    end
endmodule
