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

    // Synchronous, write-first single-port RAM:
    //   - on we=1, mem[addr] is updated with din, and dout is forwarded
    //     din directly on the same edge (so a simultaneous write+read of
    //     the same address returns the NEW data, not the stale value).
    //   - on we=0, dout is simply the registered read of mem[addr].
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