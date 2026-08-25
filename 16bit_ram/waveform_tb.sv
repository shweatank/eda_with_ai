`timescale 1ns/1ps

module waveform_tb;
    reg clk = 0;
    reg write_enable = 0;
    reg [7:0] address = 0;
    reg [15:0] write_data = 0;
    wire [15:0] read_data;

    simple_ram_16bit dut (
        .clk(clk),
        .write_enable(write_enable),
        .address(address),
        .write_data(write_data),
        .read_data(read_data)
    );

    always #5 clk = ~clk;

    initial begin
        $dumpfile("ram16.vcd");
        $dumpvars(0, waveform_tb);

        #10;
        write_enable = 1;
        address = 8'h10;
        write_data = 16'hA55A;
        #10;
        write_enable = 0;
        #10;
        address = 8'h20;
        write_enable = 1;
        write_data = 16'h5AA5;
        #10;
        write_enable = 0;
        address = 8'h10;
        #10;
        $finish;
    end
endmodule
