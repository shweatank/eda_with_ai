module logic_unit (
    input  wire       a,
    input  wire       b,
    input  wire [1:0] sel,
    output reg         y
);
    always @(*) begin
        case (sel)
            2'b00: begin
                y = a & b;          // AND
            end
            2'b01: begin
                y = a | b;          // OR
            end
            2'b10: begin
                y = ~(a & b);       // NAND
            end
            2'b11: begin
                y = ~(a | b);       // NOR
            end
            default: begin
                y = 1'b0;
            end
        endcase
    end

    initial begin
        $dumpfile("logic_unit.vcd");
        $dumpvars(0, logic_unit);
    end
endmodule
