// =====================================================================
// alu.sv  --  BUGGY (failing) version
// =====================================================================
// Simple combinational 4-bit ALU.
//
//   opcode 2'b00 -> ADD   result = a + b
//   opcode 2'b01 -> SUB   result = a - b
//   opcode 2'b10 -> AND   result = a & b
//   opcode 2'b11 -> OR    result = a | b
// =====================================================================
`timescale 1ns/1ps

module alu (
    input  logic [3:0] a,
    input  logic [3:0] b,
    input  logic [1:0] opcode,
    output logic [3:0] result
);

    localparam logic [1:0] OP_ADD = 2'b00;
    localparam logic [1:0] OP_SUB = 2'b01;
    localparam logic [1:0] OP_AND = 2'b10;
    localparam logic [1:0] OP_OR  = 2'b11;

    always_comb begin
        case (opcode)
            OP_ADD : result = a + b;
            OP_SUB : result = a - b;
            OP_AND : result = a & b;
            OP_OR  : result = a & b;   // <-- BUG: OR opcode wired to AND instead of `|`
            default: result = 4'b0000;
        endcase
    end

endmodule
