// Combinational logic gates: AND, OR, NAND, NOR
module logic_gates (
    input  wire a,
    input  wire b,
    output reg  and_out,
    output reg  or_out,
    output reg  nand_out,
    output reg  nor_out
);
    always @(*) begin
        case ({a, b})
            2'b00: begin
                and_out  = 1'b0;
                or_out   = 1'b0;
                nand_out = 1'b1;
                nor_out  = 1'b1;
            end
            2'b01: begin
                and_out  = 1'b0;
                or_out   = 1'b1;
                nand_out = 1'b1;
                nor_out  = 1'b0;
            end
            2'b10: begin
                and_out  = 1'b0;
                or_out   = 1'b1;
                nand_out = 1'b1;
                nor_out  = 1'b0;
            end
            2'b11: begin
                and_out  = 1'b1;
                or_out   = 1'b1;
                nand_out = 1'b0;
                nor_out  = 1'b0;
            end
            default: begin
                and_out  = 1'b0;
                or_out   = 1'b0;
                nand_out = 1'b0;
                nor_out  = 1'b0;
            end
        endcase
    end

    initial begin
        $dumpfile("logic_gates.vcd");
        $dumpvars(0, logic_gates);
    end
endmodule