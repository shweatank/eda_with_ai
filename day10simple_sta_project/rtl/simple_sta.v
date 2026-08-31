module simple_sta (
    input  wire clk,
    input  wire rst,
    input  wire a,
    output reg  y
);

    reg q1;
    wire and_out;

    assign and_out = q1 & a;

    always @(posedge clk) begin
        if (rst) begin
            q1 <= 1'b0;
            y  <= 1'b0;
        end
        else begin
            q1 <= a;
            y  <= and_out;
        end
    end

endmodule