`timescale 1ns/1ps

module simple_ram (
    input  wire       clk,
    input  wire       write_enable,
    input  wire [15:0] address,
    input  wire [15:0] write_data,
    output reg  [15:0] read_data
);

    // 256 locations × 8 bits
    reg [15:0] memory [0:65535];


    // ========================================================
    // SYNCHRONOUS RAM
    // ========================================================

    always @(posedge clk) begin

        // WRITE
        if (write_enable)
            memory[address] <= write_data;

        // READ
        read_data <= memory[address];

    end


    // ========================================================
    // WAVEFORM DUMP
    // ========================================================

`ifdef COCOTB_SIM

    initial begin
        $dumpfile("waves/rtl.vcd");
        $dumpvars(0, simple_ram);
    end

`endif

endmodule