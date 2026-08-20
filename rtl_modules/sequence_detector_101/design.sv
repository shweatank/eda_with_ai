// Moore FSM: detects the overlapping sequence "101" on serial input `din`
// Asserts `detected` for one cycle when the pattern completes.
module sequence_detector_101 (
    input  wire clk,
    input  wire rst_n,   // async active-low reset
    input  wire din,
    output wire detected
);
    localparam S0 = 2'd0; // no match
    localparam S1 = 2'd1; // matched "1"
    localparam S2 = 2'd2; // matched "10"
    localparam S3 = 2'd3; // matched "101"

    reg [1:0] state, next_state;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= S0;
        else
            state <= next_state;
    end

    always @(*) begin
        case (state)
            S0: next_state = din ? S1 : S0;
            S1: next_state = din ? S1 : S2;
            S2: next_state = din ? S3 : S0;
            S3: next_state = din ? S1 : S2;  // overlap: reuse trailing "1"
            default: next_state = S0;
        endcase
    end

    assign detected = (state == S3);
endmodule
