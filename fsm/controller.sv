`timescale 1ns/1ps

module controller (
    input  wire clk,
    input  wire reset,
    input  wire start,
    input  wire finish,
    output reg  busy,
    output reg  done
);

    // ========================================================
    // FSM STATES
    // ========================================================

    parameter IDLE = 2'b00;
    parameter LOAD = 2'b01;
    parameter RUN  = 2'b10;
    parameter DONE = 2'b11;


    // ========================================================
    // STATE REGISTERS
    // ========================================================

    reg [1:0] current_state;
    reg [1:0] next_state;


    // ========================================================
    // STATE REGISTER
    // ========================================================

    always @(posedge clk or posedge reset) begin

        if (reset)
            current_state <= IDLE;
        else
            current_state <= next_state;

    end


    // ========================================================
    // NEXT STATE LOGIC
    // ========================================================

    always @(*) begin

        next_state = current_state;

        case (current_state)

            IDLE: begin
                if (start)
                    next_state = LOAD;
            end

            LOAD: begin
                next_state = RUN;
            end

            RUN: begin
                if (finish)
                    next_state = DONE;
            end

            DONE: begin
                next_state = IDLE;
            end

            default: begin
                next_state = IDLE;
            end

        endcase

    end


    // ========================================================
    // OUTPUT LOGIC
    // ========================================================

    always @(*) begin

        busy = 1'b0;
        done = 1'b0;

        case (current_state)

            LOAD: begin
                busy = 1'b1;
            end

            RUN: begin
                busy = 1'b1;
            end

            DONE: begin
                done = 1'b1;
            end

            default: begin
                busy = 1'b0;
                done = 1'b0;
            end

        endcase

    end


    // ========================================================
    // VCD WAVEFORM
    // ========================================================

`ifdef COCOTB_SIM

    initial begin
        $dumpfile("waves/rtl.vcd");
        $dumpvars(0, controller);
    end

`endif

endmodule