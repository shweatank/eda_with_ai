module ram8_16_32 #(
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = 8
)(
    input  wire                  clk,
    input  wire                  we,
    input  wire [ADDR_WIDTH-1:0] addr,
    input  wire [DATA_WIDTH-1:0] din,
    output reg  [DATA_WIDTH-1:0] dout
);

    localparam DEPTH = 1 << ADDR_WIDTH;

    reg [DATA_WIDTH-1:0] mem [0:DEPTH-1];

    always @(posedge clk) begin
        if (we) begin
            mem[addr] <= din;
            dout      <= din;
        end else begin
            dout <= mem[addr];
        end
    end

    initial begin
        $dumpfile("ram8_16_32.vcd");
        $dumpvars(0, ram8_16_32);
    end

endmodule
