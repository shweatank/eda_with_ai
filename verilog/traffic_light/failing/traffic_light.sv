// =====================================================================
// traffic_light.sv  --  BUGGY (failing) version
// =====================================================================
// Simple 4-state traffic light FSM with a dwell counter.
//
//   A_GREEN  -> A_YELLOW -> B_GREEN  -> B_YELLOW -> A_GREEN ...
//
// Green states last GREEN_TICKS clock cycles, yellow states last
// YELLOW_TICKS clock cycles.
// =====================================================================
`timescale 1ns/1ps

module traffic_light (
    input  logic       clk,
    input  logic       rst_n,
    output logic [1:0] state_out,
    output logic [2:0] counter_out,
    output logic       a_green,
    output logic       a_yellow,
    output logic       b_green,
    output logic       b_yellow
);

    // ---------------- state encoding ----------------
    localparam logic [1:0] S_A_GREEN  = 2'd0;
    localparam logic [1:0] S_A_YELLOW = 2'd1;
    localparam logic [1:0] S_B_GREEN  = 2'd2;
    localparam logic [1:0] S_B_YELLOW = 2'd3;

    // ---------------- dwell times -------------------
    localparam int GREEN_TICKS  = 2;   // <-- BUG: should be 4, green ends far too early
    localparam int YELLOW_TICKS = 2;   // <-- correct yellow duration

    logic [1:0] state;
    logic [2:0] counter;

    // dwell limit for the current state
    logic [2:0] limit;
    always_comb begin
        case (state)
            S_A_GREEN  : limit = GREEN_TICKS[2:0];
            S_A_YELLOW : limit = YELLOW_TICKS[2:0];
            S_B_GREEN  : limit = GREEN_TICKS[2:0];
            S_B_YELLOW : limit = YELLOW_TICKS[2:0];
            default    : limit = GREEN_TICKS[2:0];
        endcase
    end

    // next state in the ring
    logic [1:0] nxt;
    always_comb begin
        case (state)
            S_A_GREEN  : nxt = S_A_YELLOW;
            S_A_YELLOW : nxt = S_B_GREEN;
            S_B_GREEN  : nxt = S_B_YELLOW;
            S_B_YELLOW : nxt = S_A_GREEN;
            default    : nxt = S_A_GREEN;
        endcase
    end

    // ---------------- sequential logic --------------
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state   <= S_A_GREEN;
            counter <= 3'd0;
        end else begin
            if (counter == (limit - 3'd1)) begin
                state   <= nxt;
                counter <= 3'd0;
            end else begin
                counter <= counter + 3'd1;
            end
        end
    end

    // ---------------- outputs -----------------------
    assign state_out   = state;
    assign counter_out = counter;
    assign a_green     = (state == S_A_GREEN);
    assign a_yellow    = (state == S_A_YELLOW);
    assign b_green     = (state == S_B_GREEN);
    assign b_yellow    = (state == S_B_YELLOW);

endmodule
