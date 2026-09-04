// =====================================================================
// traffic_light_tb.sv -- GOLDEN testbench (identical for passing/failing)
// =====================================================================
// This testbench is the SOURCE OF TRUTH for PASS/FAIL.
// It is byte-for-byte identical in the passing/ and failing/ folders;
// only the RTL under test differs.
//
// Machine-parsable log format:
//     TEST_<n>: PASS|FAIL
//     NAME: <test name>
//     EXPECTED: <value>
//     ACTUAL: <value>
//     MESSAGE: <human readable note>
//     ...
//     TOTAL_TESTS: <n>
//     PASSED: <n>
//     FAILED: <n>
//     STATUS: PASSED|FAILED
// =====================================================================
`timescale 1ns/1ps

module traffic_light_tb;

    logic       clk;
    logic       rst_n;
    logic [1:0] state_out;
    logic [2:0] counter_out;
    logic       a_green, a_yellow, b_green, b_yellow;

    int total_tests = 0;
    int passed_tests = 0;
    int failed_tests = 0;
    int cycle_count = 0;   // active clock edges since reset release

    // ---------------- DUT ----------------
    traffic_light dut (
        .clk         (clk),
        .rst_n       (rst_n),
        .state_out   (state_out),
        .counter_out (counter_out),
        .a_green     (a_green),
        .a_yellow    (a_yellow),
        .b_green     (b_green),
        .b_yellow    (b_yellow)
    );

    // ---------------- clock: 10ns period ----------------
    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end

    // ---------------- state decoding ----------------
    function automatic string state_name(input logic [1:0] s);
        case (s)
            2'd0: state_name = "A_GREEN";
            2'd1: state_name = "A_YELLOW";
            2'd2: state_name = "B_GREEN";
            2'd3: state_name = "B_YELLOW";
            default: state_name = "UNKNOWN";
        endcase
    endfunction

    // ---------------- scoreboard ----------------
    task automatic check(input int          id,
                         input string       name,
                         input string       expected,
                         input string       actual,
                         input string       message);
        total_tests++;
        if (expected == actual) begin
            passed_tests++;
            $display("TEST_%0d: PASS", id);
        end else begin
            failed_tests++;
            $display("TEST_%0d: FAIL", id);
        end
        $display("NAME: %s", name);
        $display("EXPECTED: %s", expected);
        $display("ACTUAL: %s", actual);
        $display("MESSAGE: %s", message);
        $display("");
    endtask

    // advance the simulation until `target` active clock edges have
    // happened since reset was released, then settle 1ns before sampling
    task automatic run_to_cycle(input int target);
        while (cycle_count < target) begin
            @(posedge clk);
            if (rst_n) cycle_count++;
        end
        #1;
    endtask

    // ---------------- stimulus ----------------
    initial begin
        $dumpfile("waveform.vcd");
        $dumpvars(0, traffic_light_tb);

        $display("========================================");
        $display("TRAFFIC LIGHT CONTROLLER VERIFICATION");
        $display("========================================");
        $display("");

        // ---- hold reset for 2 full clock periods ----
        rst_n = 1'b0;
        @(negedge clk);
        @(negedge clk);
        #1;

        // ---- TEST 1: reset behaviour ----
        check(1, "Reset",
              "A_GREEN/0",
              $sformatf("%s/%0d", state_name(state_out), counter_out),
              "Asserting rst_n must force the FSM to A_GREEN with the dwell counter cleared");

        // ---- release reset ----
        @(negedge clk);
        rst_n = 1'b1;

        // ---- TEST 2: A_GREEN still active on the 1st cycle ----
        run_to_cycle(1);
        check(2, "A_GREEN",
              "A_GREEN",
              state_name(state_out),
              "One cycle after reset release the FSM must still be dwelling in A_GREEN");

        // ---- TEST 3: A_GREEN lasts 4 cycles, then A_YELLOW ----
        run_to_cycle(4);
        check(3, "A_YELLOW",
              "A_YELLOW",
              state_name(state_out),
              "A_GREEN must dwell for 4 cycles, so cycle 4 must be A_YELLOW");

        // ---- TEST 4: A_YELLOW lasts 2 cycles, then B_GREEN ----
        run_to_cycle(6);
        check(4, "B_GREEN",
              "B_GREEN",
              state_name(state_out),
              "A_YELLOW must dwell for 2 cycles, so cycle 6 must be B_GREEN");

        // ---- run a little longer so the waveform is interesting ----
        run_to_cycle(14);

        // ---------------- summary ----------------
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

    // ---------------- global timeout ----------------
    initial begin
        #10000;
        $display("MESSAGE: SIMULATION TIMEOUT");
        $display("STATUS: FAILED");
        $finish;
    end

endmodule
