module controller (
    input wire clk,
    input wire reset,
    input wire start,
    input wire finish,
    output reg busy,
    output reg done
);

parameter IDLE = 2'b00;
parameter LOAD = 2'b01;
parameter RUN  = 2'b10;
parameter DONE = 2'b11;

reg [1:0] current_state;
reg [1:0] next_state;


// VCD waveform generation
initial begin
    $dumpfile("controller.vcd");
    $dumpvars(0, controller);
end


// State Register
always @(posedge clk or posedge reset) begin
    if (reset)
        current_state <= IDLE;
    else
        current_state <= next_state;
end


// Next State Logic
always @(*) begin
    next_state = current_state;

    case (current_state)

        IDLE:
            if (start)
                next_state = LOAD;

        LOAD:
            next_state = RUN;

        RUN:
            if (finish)
                next_state = DONE;

        DONE:
            next_state = IDLE;

        default:
            next_state = IDLE;

    endcase
end


// Output Logic
always @(*) begin

    busy = 1'b0;
    done = 1'b0;

    case (current_state)

        LOAD: busy = 1'b1;

        RUN: busy = 1'b1;

        DONE: done = 1'b1;

    endcase

end

endmodule