`timescale 1ns/1ps

module uart (
    input clk,
    input rst,
    input data_in,
    output reg data_out
);

always @(posedge clk or posedge rst) begin
    if (rst) begin
        data_out <= 1'b0;
    end else begin
        data_out <= data_in;
    end
end



endmodule
