// 4-bit Up/Down Counter with sync active-high reset and enable
module updown_counter4 (
    input  wire       clk,
    input  wire       rst,      // sync active-high reset
    input  wire       en,       // count enable
    input  wire       up_down,  // 1 = count up, 0 = count down
    output reg  [3:0] count
);
    always @(posedge clk) begin
        if (rst)
            count <= 4'b0000;
        else if (en) begin
            if (up_down)
                count <= count + 1'b1;
            else
                count <= count - 1'b1;
        end
    end
endmodule
