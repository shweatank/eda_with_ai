module vector_and (
    input wire [7:0] a,
    input wire [7:0] b,
    output wire [7:0] y
);

genvar i;

generate
    for (i = 0; i < 8; i = i + 1) begin : GEN_AND
        assign y[i] = a[i] & b[i];
    end
endgenerate

initial begin
    $dumpfile("vector_and.vcd");
    $dumpvars(0, vector_and);
end

endmodule