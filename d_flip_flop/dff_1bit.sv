module dff_1bit (
    input  wire clk,
    input  wire d,
    output reg  q
);

    always @(posedge clk) begin
        q <= d;
    end

    initial begin
        $dumpfile("dff_1bit.vcd");
        $dumpvars(0, dff_1bit);
    end

endmodule
