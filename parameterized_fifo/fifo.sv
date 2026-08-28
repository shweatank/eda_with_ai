module parameterized_fifo #(
    parameter DATA_WIDTH = 8,
    parameter FIFO_DEPTH = 8
)(
    input wire clk,
    input wire reset,
    input wire write_enable,
    input wire read_enable,
    input wire [DATA_WIDTH-1:0] write_data,
    output reg [DATA_WIDTH-1:0] read_data,
    output wire full,
    output wire empty,
    output wire [$clog2(FIFO_DEPTH+1)-1:0] count,
    output reg overflow,
    output reg underflow
);
    localparam PTR_WIDTH = (FIFO_DEPTH <= 2) ? 1 : $clog2(FIFO_DEPTH);
    localparam COUNT_WIDTH = $clog2(FIFO_DEPTH + 1);

    reg [DATA_WIDTH-1:0] memory [0:FIFO_DEPTH-1];
    reg [PTR_WIDTH-1:0] write_pointer;
    reg [PTR_WIDTH-1:0] read_pointer;
    reg [COUNT_WIDTH-1:0] count_register;

    assign count = count_register;
    assign full = (count_register == FIFO_DEPTH);
    assign empty = (count_register == 0);

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            write_pointer <= 0;
            read_pointer <= 0;
            count_register <= 0;
            read_data <= 0;
            overflow <= 0;
            underflow <= 0;
        end else begin
            overflow <= write_enable && full;
            underflow <= read_enable && empty;

            if (write_enable && !full) begin
                memory[write_pointer] <= write_data;
                if (write_pointer == FIFO_DEPTH - 1)
                    write_pointer <= 0;
                else
                    write_pointer <= write_pointer + 1'b1;
            end

            if (read_enable && !empty) begin
                read_data <= memory[read_pointer];
                if (read_pointer == FIFO_DEPTH - 1)
                    read_pointer <= 0;
                else
                    read_pointer <= read_pointer + 1'b1;
            end

            case ({write_enable && !full, read_enable && !empty})
                2'b10: count_register <= count_register + 1'b1;
                2'b01: count_register <= count_register - 1'b1;
                default: count_register <= count_register;
            endcase
        end
    end
endmodule
