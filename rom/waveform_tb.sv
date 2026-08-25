`timescale 1ns/1ps

module waveform_tb;
    reg [2:0] address = 0;
    wire [7:0] data;

    rom dut (
        .address(address),
        .data(data)
    );

    initial begin
        $dumpfile("rom.vcd");
        $dumpvars(0, waveform_tb);

        #10 address = 3'd1;
        #10 address = 3'd2;
        #10 address = 3'd3;
        #10 address = 3'd4;
        #10 address = 3'd5;
        #10 address = 3'd6;
        #10 address = 3'd7;
        #10 $finish;
    end
endmodule
