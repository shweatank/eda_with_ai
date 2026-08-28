`timescale 1ns/1ps

module waveform_tb;
    reg clk = 0;
    reg reset = 1;
    reg write_enable = 0;
    reg read_enable = 0;
    reg [7:0] write_data = 0;
    wire [7:0] read_data;
    wire full, empty, overflow, underflow;
    wire [3:0] count;

    parameterized_fifo #(.DATA_WIDTH(8), .FIFO_DEPTH(8)) dut (
        .clk(clk), .reset(reset), .write_enable(write_enable), .read_enable(read_enable),
        .write_data(write_data), .read_data(read_data), .full(full), .empty(empty),
        .count(count), .overflow(overflow), .underflow(underflow)
    );

    always #5 clk = ~clk;

    initial begin
        $dumpfile("fifo.vcd");
        $dumpvars(0, waveform_tb);
        #12 reset = 0;
        #8 write_enable = 1; write_data = 8'h11;
        #10 write_data = 8'h22;
        #10 write_data = 8'h33;
        #10 write_enable = 0; read_enable = 1;
        #80 $finish;
    end
endmodule
