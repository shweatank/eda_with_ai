module alu (
    input  [7:0]  a,
    input  [7:0]  b,
    input  [1:0]  op,        // 00=add, 01=sub, 10=mul, 11=div
    output reg [15:0] result,    // wide enough to hold the largest case (multiply)
    output reg [7:0]  remainder, // only meaningful for divide
    output reg div_by_zero
);

    localparam ADD = 2'b00;
    localparam SUB = 2'b01;
    localparam MUL = 2'b10;
    localparam DIV = 2'b11;

    always @(*) begin
        // Defaults every cycle to avoid inferred latches
        result      = 16'd0;
        remainder   = 8'd0;
        div_by_zero = 1'b0;

        case (op)
            ADD: result = {7'd0, a} + {7'd0, b};       // 9-bit-equivalent sum, zero-extended
            SUB: result = {{8{1'b0}}, a} - {{8{1'b0}}, b}; // treated as unsigned wraparound; see note below
            MUL: result = a * b;                        // full 16-bit product
            DIV: begin
                if (b == 0) begin
                    div_by_zero = 1'b1;
                    result      = 16'd0;
                    remainder   = 8'd0;
                end else begin
                    result    = {8'd0, a / b};  // quotient in lower 8 bits
                    remainder = a % b;
                end
            end
            default: result = 16'd0;
        endcase
    end

    initial begin
        $dumpfile("alu.vcd");
        $dumpvars(0, alu);
    end

endmodule