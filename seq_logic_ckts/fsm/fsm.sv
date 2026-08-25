module controller (
    input wire clk,
    input wire reset,
    input wire start,
    input wire finish,
    output reg busy,
    output reg done
);

    parameter [1:0] IDLE = 2'b00;
    parameter [1:0] LOAD = 2'b01;
    parameter [1:0] RUN  = 2'b10;
    parameter [1:0] DONE = 2'b11;

    reg [1:0] current_state;
    reg [1:0] next_state;

    // State register
    always @(posedge clk or posedge reset) begin
        if (reset)
            current_state <= IDLE;
        else
            current_state <= next_state;
    end

    // Next-state logic
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

    // Output logic
    always @(*) begin
        busy = 1'b0;
        done = 1'b0;
        case (current_state)
            LOAD, RUN: begin
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

endmodule