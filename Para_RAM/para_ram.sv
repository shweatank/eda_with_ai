module para_ram #(
    parameter ADDR_WIDTH = 8,     // 2^ADDR_WIDTH = number of locations
    parameter DATA_WIDTH = 8      // bits per location
)(
    input  wire                    clk,
    input  wire                    write_enable,
    input  wire [ADDR_WIDTH-1:0]   address,
    input  wire [DATA_WIDTH-1:0]   write_data,
    output reg  [DATA_WIDTH-1:0]   read_data
);
    reg [DATA_WIDTH-1:0] memory [0:(2**ADDR_WIDTH)-1];

    always @(posedge clk) begin
        if (write_enable)
            memory[address] <= write_data;
        read_data <= memory[address];
    end

    initial begin
        $dumpfile("para_ram.vcd");
        $dumpvars(0, para_ram);
    end
endmodule
