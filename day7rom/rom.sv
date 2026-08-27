module rom (
    input  wire [2:0] address,
    output reg  [7:0] data
);

    always @(*) begin
        case (address)
            3'd0: data = 8'h11;
            3'd1: data = 8'h22;
            3'd2: data = 8'h33;
            3'd3: data = 8'h44;
            3'd4: data = 8'h55;
            3'd5: data = 8'h66;
            3'd6: data = 8'h77;
            3'd7: data = 8'h88;
        endcase
    end

endmodule