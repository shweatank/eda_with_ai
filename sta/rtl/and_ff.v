module and_ff (
    input  wire clk,
    input  wire reset,
    input  wire a,
    input  wire b,
    output reg  y
);

always @(posedge clk or posedge reset) begin
    if (reset)
        y <= 1'b0;
    else
        y <= a & b;
end

endmodule
