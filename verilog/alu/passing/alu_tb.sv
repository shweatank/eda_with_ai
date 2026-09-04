// =====================================================================
// alu_tb.sv -- GOLDEN testbench (identical for passing/failing)
// =====================================================================
// This testbench is the SOURCE OF TRUTH for PASS/FAIL.
// It is byte-for-byte identical in the passing/ and failing/ folders;
// only the RTL under test differs.
// =====================================================================
`timescale 1ns/1ps

module alu_tb;

    logic       clk;
    logic [3:0] a, b;
    logic [1:0] opcode;
    logic [3:0] result;

    int total_tests  = 0;
    int passed_tests = 0;
    int failed_tests = 0;

    // ---------------- DUT ----------------
    alu dut (
        .a      (a),
        .b      (b),
        .opcode (opcode),
        .result (result)
    );

    // clock only exists so the VCD has a time axis to browse
    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end

    function automatic string op_name(input logic [1:0] op);
        case (op)
            2'b00: op_name = "ADD";
            2'b01: op_name = "SUB";
            2'b10: op_name = "AND";
            2'b11: op_name = "OR";
            default: op_name = "UNKNOWN";
        endcase
    endfunction

    // apply one operation and score it
    task automatic run_op(input int         id,
                          input logic [1:0] op,
                          input logic [3:0] av,
                          input logic [3:0] bv,
                          input logic [3:0] exp);
        a      = av;
        b      = bv;
        opcode = op;
        @(posedge clk);
        #1;

        total_tests++;
        if (result === exp) begin
            passed_tests++;
            $display("TEST_%0d: PASS", id);
        end else begin
            failed_tests++;
            $display("TEST_%0d: FAIL", id);
        end
        $display("NAME: %s", op_name(op));
        $display("EXPECTED: %0d", exp);
        $display("ACTUAL: %0d", result);
        $display("MESSAGE: opcode=%0s A=%0d B=%0d -> result[3:0] must be %0d",
                 op_name(op), av, bv, exp);
        $display("");
    endtask

    initial begin
        $dumpfile("waveform.vcd");
        $dumpvars(0, alu_tb);

        $display("========================================");
        $display("4-BIT ALU VERIFICATION");
        $display("========================================");
        $display("");

        a = 4'd0; b = 4'd0; opcode = 2'b00;
        @(negedge clk);

        run_op(1, 2'b00, 4'd5, 4'd3, 4'd8);   // ADD : 5 + 3 = 8
        run_op(2, 2'b01, 4'd7, 4'd2, 4'd5);   // SUB : 7 - 2 = 5
        run_op(3, 2'b10, 4'd6, 4'd3, 4'd2);   // AND : 6 & 3 = 2
        run_op(4, 2'b11, 4'd6, 4'd3, 4'd7);   // OR  : 6 | 3 = 7

        @(posedge clk);
        @(posedge clk);

        $display("========================================");
        $display("TOTAL_TESTS: %0d", total_tests);
        $display("PASSED: %0d", passed_tests);
        $display("FAILED: %0d", failed_tests);
        if (failed_tests == 0)
            $display("STATUS: PASSED");
        else
            $display("STATUS: FAILED");
        $display("========================================");

        $finish;
    end

    initial begin
        #10000;
        $display("MESSAGE: SIMULATION TIMEOUT");
        $display("STATUS: FAILED");
        $finish;
    end

endmodule
