module alu (
    input  wire signed [7:0] A,
    input  wire signed [7:0] B,
    input  wire [1:0] OP,

    output reg signed [7:0] Result,
    output reg Overflow
);

always @(*) begin

    // Default values
    Result = 8'sd0;
    Overflow = 1'b0;

    case (OP)

        2'b00: begin

            Result = A + B;

            Overflow = (~(A[7] ^ B[7])) &
                       (Result[7] ^ A[7]);

        end

        2'b01: begin

            Result = A - B;

            Overflow = (A[7] ^ B[7]) &
                       (Result[7] ^ A[7]);

        end

        2'b10: begin

            Result = A * B;

            if ((A * B) < -128 || (A * B) > 127) begin
                Overflow = 1'b1;
            end
            else begin
                Overflow = 1'b0;
            end

        end


        2'b11: begin

            if (B == 0) begin

                Result = 8'sd0;
                Overflow = 1'b1;

            end
            else begin

                Result = A / B;
                Overflow = 1'b0;

            end

        end

        default: begin

            Result = 8'sd0;
            Overflow = 1'b0;

        end

    endcase

end

endmodule