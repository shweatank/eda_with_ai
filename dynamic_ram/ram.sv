module dynamic_ram #(
    parameter DATA_WIDTH = 8,
    parameter ADDRESS_WIDTH = 8
)(
    input wire clk,
    input wire write_enable,
    input wire [ADDRESS_WIDTH-1:0] address,
    input wire [DATA_WIDTH-1:0] write_data,
    output reg [DATA_WIDTH-1:0] read_data
);
    reg [DATA_WIDTH-1:0] memory [0:(1 << ADDRESS_WIDTH)-1];

    always @(posedge clk) begin
        if (write_enable)
            memory[address] <= write_data;
        read_data <= memory[address];
    end
endmodule
