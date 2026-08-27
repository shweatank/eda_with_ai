module vector_and #(
    parameter WIDTH = 8
)(
    input wire [WIDTH-1:0] a,
    input wire [WIDTH-1:0] b,
    output wire [WIDTH-1:0] y
);

    genvar i;

    generate
        for (i = 0; i < WIDTH; i = i + 1) begin : GEN_AND
            assign y[i] = a[i] & b[i];
        end
    endgenerate

    initial begin
        $dumpfile("vector_and.vcd");
        $dumpvars(0, vector_and);
    end

endmodule