module simple_ram_16bit (
    input wire clk,
    input wire write_enable,
    input wire [7:0] address,
    input wire [15:0] write_data,
    output reg [15:0] read_data
);
    reg [15:0] memory [0:255];

    always @(posedge clk) begin
        if (write_enable)
            memory[address] <= write_data;
        read_data <= memory[address];
    end
endmodule
