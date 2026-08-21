module arithmetic (
    input  wire [7:0]  a,
    input  wire [7:0]  b,

    output wire [7:0]  sum,         // a + b
    output wire [7:0]  diff,        // a - b
    output wire [15:0] product,     // a * b
    output wire [7:0]  quotient,    // a / b
    output wire [7:0]  remainder    // a % b
);
    assign sum       = a + b;
    assign diff      = a - b;
    assign product   = a * b;
    assign quotient  = a / b;   // undefined (X) if b == 0
    assign remainder = a % b;   // undefined (X) if b == 0

    initial begin
        $dumpfile("arithmetic.vcd");
        $dumpvars(0, arithmetic);
    end
endmodule
