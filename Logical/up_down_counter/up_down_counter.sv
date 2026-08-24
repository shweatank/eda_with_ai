module up_down_counter (
    input wire clk,
    input wire reset,
    input wire up,
    output reg [7:0] count
);

    always @(posedge clk or posedge reset) begin
        if (reset)
            count <= 8'd0;
        else if (up)
            count <= count + 1'b1;
        else
            count <= count - 1'b1;
    end

endmodule
