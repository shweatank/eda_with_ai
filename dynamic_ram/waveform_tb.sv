`timescale 1ns/1ps

module waveform_tb;
    reg clk = 0;
    reg write_enable = 0;
    reg [7:0] address = 0;
    reg [7:0] write_data = 0;
    wire [7:0] read_data;

    dynamic_ram #(.DATA_WIDTH(8), .ADDRESS_WIDTH(8)) dut (
        .clk(clk),
        .write_enable(write_enable),
        .address(address),
        .write_data(write_data),
        .read_data(read_data)
    );

    always #5 clk = ~clk;

    initial begin
        $dumpfile("ram.vcd");
        $dumpvars(0, waveform_tb);
        #7 write_enable = 1; address = 8'h10; write_data = 8'hA5;
        #10 address = 8'h20; write_data = 8'h5A;
        #10 address = 8'hFF; write_data = 8'hC3;
        #10 write_enable = 0; address = 8'h10;
        #10 address = 8'h20;
        #10 address = 8'hFF;
        #10 $finish;
    end
endmodule
