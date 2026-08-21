module arithmetic_all (
    input  wire [7:0] a_u,
    input  wire [7:0] b_u,
    input  wire signed [7:0] a_s,
    input  wire signed [7:0] b_s,
    input  wire [2:0] op,

    output reg [15:0] u_result,
    output reg signed [15:0] s_result
);

    always @(*) begin
        u_result = 16'd0;
        s_result = 16'sd0;

        case (op)
            3'd0: begin // sum
                u_result = a_u + b_u;
                s_result = a_s + b_s;
            end
            3'd1: begin // sub
                u_result = a_u - b_u;
                s_result = a_s - b_s;
            end
            3'd2: begin // mul
                u_result = a_u * b_u;
                s_result = a_s * b_s;
            end
            3'd3: begin // div
                if (b_u == 8'd0)
                    u_result = 16'd0;
                else
                    u_result = a_u / b_u;

                if (b_s == 8'sd0)
                    s_result = 16'sd0;
                else
                    s_result = a_s / b_s;
            end
            3'd4: begin // remainder
                if (b_u == 8'd0)
                    u_result = a_u;
                else
                    u_result = a_u % b_u;

                if (b_s == 8'sd0)
                    s_result = a_s;
                else
                    s_result = a_s % b_s;
            end
            default: begin
                u_result = 16'd0;
                s_result = 16'sd0;
            end
        endcase
    end

endmodule

