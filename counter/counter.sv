module counter #(
    parameter WIDTH = 8
)(
    input  wire              clk,
    input  wire              reset,
    output reg  [WIDTH-1:0]  count
);
    always @(posedge clk or posedge reset) begin
        if (reset)
            count <= {WIDTH{1'b0}};
        else
            count <= count + 1'b1;
    end

    initial begin
        $dumpfile("counter.vcd");
        $dumpvars(0, counter);
    end
endmodule
