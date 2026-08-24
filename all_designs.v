module and_gate (input a, input b, output y);
    assign y = a & b;
    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, and_gate);
    end
endmodule

module or_gate (input a, input b, output y);
    assign y = a | b;
    initial begin
        $dumpfile("dump_or.vcd");
        $dumpvars(0, or_gate);
    end
endmodule

module not_gate (input a, output y);
    assign y = ~a;
    initial begin
        $dumpfile("dump_not.vcd");
        $dumpvars(0, not_gate);
    end
endmodule

module xor_gate (input a, input b, output y);
    assign y = a ^ b;
    initial begin
        $dumpfile("dump_xor.vcd");
        $dumpvars(0, xor_gate);
    end
endmodule

module nand_gate (input a, input b, output y);
    assign y = ~(a & b);
    initial begin
        $dumpfile("dump_nand.vcd");
        $dumpvars(0, nand_gate);
    end
endmodule

module nor_gate (input a, input b, output y);
    assign y = ~(a | b);
    initial begin
        $dumpfile("dump_nor.vcd");
        $dumpvars(0, nor_gate);
    end
endmodule

module xnor_gate (input a, input b, output y);
    assign y = ~(a ^ b);
    initial begin
        $dumpfile("dump_xnor.vcd");
        $dumpvars(0, xnor_gate);
    end
endmodule

// designs.v
// All modules for the GUI, in one file -- same pattern as all_designs.v.
// The Makefile's TOPLEVEL is overridden per-run to pick which module to
// elaborate as the simulation top.

module logic_model (
    input  a,
    input  b,
    input  c,
    output y
);
    assign y = (a & b) | c;

    initial begin
        $dumpfile("logic_model.vcd");
        $dumpvars(0, logic_model);
    end
endmodule


module adder (
    input  [7:0] a,
    input  [7:0] b,
    output [8:0] y
);
    assign y = a + b;

    initial begin
        $dumpfile("adder.vcd");
        $dumpvars(0, adder);
    end
endmodule


module subtractor (
    input  [7:0] a,
    input  [7:0] b,
    output [8:0] y   // interpret as signed two's complement in the testbench
);
    assign y = a - b;

    initial begin
        $dumpfile("subtractor.vcd");
        $dumpvars(0, subtractor);
    end
endmodule


module multiplier (
    input  [7:0] a,
    input  [7:0] b,
    output [15:0] y
);
    assign y = a * b;

    initial begin
        $dumpfile("multiplier.vcd");
        $dumpvars(0, multiplier);
    end
endmodule


module divider (
    input  [7:0] a,
    input  [7:0] b,
    output [7:0] quotient,
    output [7:0] remainder,
    output div_by_zero
);
    assign quotient    = (b == 0) ? 8'd0 : a / b;
    assign remainder   = (b == 0) ? 8'd0 : a % b;
    assign div_by_zero = (b == 0);

    initial begin
        $dumpfile("divider.vcd");
        $dumpvars(0, divider);
    end
endmodule


module alu (
    input  [7:0]  a,
    input  [7:0]  b,
    input  [1:0]  op,        // 00=add, 01=sub, 10=mul, 11=div
    output reg [15:0] result,
    output reg [7:0]  remainder,
    output reg div_by_zero
);
    localparam ADD = 2'b00;
    localparam SUB = 2'b01;
    localparam MUL = 2'b10;
    localparam DIV = 2'b11;

    always @(*) begin
        result      = 16'd0;
        remainder   = 8'd0;
        div_by_zero = 1'b0;

        case (op)
            ADD: result = a + b;
            SUB: result = a - b;
            MUL: result = a * b;
            DIV: begin
                if (b == 0) begin
                    div_by_zero = 1'b1;
                end else begin
                    result    = {8'd0, a / b};
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


module dff_1bit (
    input  wire clk,
    input  wire reset,
    input  wire d,
    output reg  q
);

    // Asynchronous active-high reset
    always @(posedge clk or posedge reset) begin
        if (reset)
            q <= 1'b0;
        else
            q <= d;
    end

    // Waveform generation for simulation only
    initial begin
        $dumpfile("dff_waveform.vcd");
        $dumpvars(0, dff_1bit);
    end

endmodule
