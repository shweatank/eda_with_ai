module adder (
    input  wire [0:7] A,
    input  wire [0:7] B,
    output wire [0:7] Sum,
    output wire       Cout,
    output wire       Overflow
);

assign {Cout, Sum} = A + B;

assign Overflow = (~(A[7] ^ B[7])) & (Sum[7] ^ A[7]);

initial begin
    $dumpfile("dump.vcd");
    $dumpvars(0, adder);
end
endmodule