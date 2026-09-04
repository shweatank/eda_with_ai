module ram8 (
    input logic clk,
    input logic we,
    input logic [2:0] addr,
    input logic [7:0] din,
    output logic [7:0] dout
);
    logic [7:0] mem [0:7];

    always_ff @(posedge clk) begin
        if (we) mem[addr] <= din;
        dout <= mem[addr];
    end
endmodule
