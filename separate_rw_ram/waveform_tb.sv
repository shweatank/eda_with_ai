`timescale 1ns/1ps

module waveform_tb;
    reg clk = 0;
    reg write_enable = 0;
    reg [7:0] write_address = 0;
    reg [7:0] read_address = 0;
    reg [15:0] write_data = 0;
    wire [15:0] read_data;

    ram dut (
        .clk(clk),
        .write_enable(write_enable),
        .write_address(write_address),
        .read_address(read_address),
        .write_data(write_data),
        .read_data(read_data)
    );

    always #5 clk = ~clk;

    initial begin
        $dumpfile("ram.vcd");
        $dumpvars(0, waveform_tb);

        #10;
        write_enable = 1;
        write_address = 8'h10;
        read_address = 8'h20;
        write_data = 16'hA55A;
        #10;
        write_enable = 0;
        read_address = 8'h10;
        #10;
        write_enable = 1;
        write_address = 8'h20;
        read_address = 8'h10;
        write_data = 16'h5AA5;
        #10;
        write_enable = 0;
        read_address = 8'h20;
        #10;
        read_address = 8'h10;
        #10;
        $finish;
    end
endmodule
