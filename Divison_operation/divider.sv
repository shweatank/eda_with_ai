// File: files_divider/divider.sv
module divider #(parameter WIDTH = 4) (
    input  logic [WIDTH-1:0] a,         // Dividend (Numerator)
    input  logic [WIDTH-1:0] b,         // Divisor (Denominator)
    output logic [WIDTH-1:0] quotient,  // Result of a / b
    output logic [WIDTH-1:0] remainder, // Result of a % b
    output logic             div_by_zero // Flag if divisor is 0
);

    // Div-by-zero detection flag
    assign div_by_zero = (b == '0);

    // Combinational division and modulo logic
    // Hardware guards against division by zero by outputting all 1s or 0s if b == 0
    assign quotient  = div_by_zero ? {WIDTH{1'b1}} : (a / b);
    assign remainder = div_by_zero ? a             : (a % b);

endmodule

// Simulation testbench wrapper (Automatically ignored by Yosys during synthesis)
`ifndef SYNTHESIS
module tb_divider;
    parameter WIDTH = 4;
    logic [WIDTH-1:0] a, b;
    logic [WIDTH-1:0] quotient;
    logic [WIDTH-1:0] remainder;
    logic             div_by_zero;

    divider #(.WIDTH(WIDTH)) uut (
        .a(a), .b(b),
        .quotient(quotient), .remainder(remainder),
        .div_by_zero(div_by_zero)
    );

    initial begin
        $dumpfile("divider.vcd");
        $dumpvars(0, tb_divider);

        $display("Time\ta    b    | quotient remainder div_zero");
        $display("--------------------------------------------");

        // Test 1: Normal division (7 / 2 = 3, remainder 1)
        a = 4'b0111; b = 4'b0010; #10;
        $display("%0t\t%b  %b    | %b        %b         %b", $time, a, b, quotient, remainder, div_by_zero);

        // Test 2: Exact division (8 / 4 = 2, remainder 0)
        a = 4'b1000; b = 4'b0100; #10;
        $display("%0t\t%b  %b    | %b        %b         %b", $time, a, b, quotient, remainder, div_by_zero);

        // Test 3: Division by Zero (5 / 0)
        a = 4'b0101; b = 4'b0000; #10;
        $display("%0t\t%b  %b    | %b        %b         %b", $time, a, b, quotient, remainder, div_by_zero);

        $finish;
    end
endmodule
`endif
