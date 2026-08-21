// File: files_half_adder/half_adder.sv
module half_adder (
    input  logic a,
    input  logic b,
    output logic sum,
    output logic carry
);

    // Half adder logic equations
    assign sum   = a ^ b; // XOR gate for Sum
    assign carry = a & b; // AND gate for Carry

endmodule

// Simulation testbench wrapper
`ifndef SYNTHESIS
module tb_half_adder;
    logic a, b;
    logic sum, carry;

    // Instantiate DUT (Device Under Test)
    half_adder uut (
        .a(a), 
        .b(b), 
        .sum(sum), 
        .carry(carry)
    );

    initial begin
        $dumpfile("half_adder.vcd");
        $dumpvars(0, tb_half_adder);

        $display("Time\tA B | Sum Carry");
        $display("-------------------");

        // Truth Table Test Cases
        a = 0; b = 0; #10;
        $display("%0t\t%b %b |  %b     %b", $time, a, b, sum, carry);

        a = 0; b = 1; #10;
        $display("%0t\t%b %b |  %b     %b", $time, a, b, sum, carry);

        a = 1; b = 0; #10;
        $display("%0t\t%b %b |  %b     %b", $time, a, b, sum, carry);

        a = 1; b = 1; #10;
        $display("%0t\t%b %b |  %b     %b", $time, a, b, sum, carry);

        $finish;
    end
endmodule
`endif
