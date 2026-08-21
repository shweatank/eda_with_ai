// File: files_logic_gates/logic_gates.sv
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
endmodule

// Simulation testbench wrapper
`ifndef SYNTHESIS
module tb_logic_gates;
    reg a, b;
    wire and_out, or_out, nand_out, nor_out;

    // Instantiate DUT (Device Under Test)
    logic_gates uut (.*);

    initial begin
        $dumpfile("logic_gates.vcd");
        $dumpvars(0, tb_logic_gates);

        $display("Time | A B | AND OR NAND NOR");
        $display("--------------------------");

        a = 0; b = 0; #10;
        $display("%0t  | %b %b |  %b   %b   %b    %b", $time, a, b, and_out, or_out, nand_out, nor_out);

        a = 0; b = 1; #10;
        $display("%0t  | %b %b |  %b   %b   %b    %b", $time, a, b, and_out, or_out, nand_out, nor_out);

        a = 1; b = 0; #10;
        $display("%0t  | %b %b |  %b   %b   %b    %b", $time, a, b, and_out, or_out, nand_out, nor_out);

        a = 1; b = 1; #10;
        $display("%0t  | %b %b |  %b   %b   %b    %b", $time, a, b, and_out, or_out, nand_out, nor_out);

        $finish;
    end
endmodule
`endif
