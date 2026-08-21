// File: files_full_adder/full_adder.sv
module full_adder (
    input  logic a,
    input  logic b,
    input  logic cin,   // Carry-in
    output logic sum,
    output logic cout   // Carry-out
);

    // Full adder logic equations
    // Sum is 1 if an odd number of inputs are 1
    assign sum  = a ^ b ^ cin;
    
    // Carry-out is 1 if two or more inputs are 1
    assign cout = (a & b) | (b & cin) | (a & cin);

endmodule

// Simulation testbench wrapper (Automatically ignored by Yosys during synthesis)
`ifndef SYNTHESIS
module tb_full_adder;
    logic a, b, cin;
    logic sum, cout;

    // Instantiate DUT (Device Under Test)
    full_adder uut (
        .a(a), 
        .b(b), 
        .cin(cin), 
        .sum(sum), 
        .cout(cout)
    );

    initial begin
        $dumpfile("full_adder.vcd");
        $dumpvars(0, tb_full_adder);

        $display("Time\tA B Cin | Sum Cout");
        $display("-----------------------");

        // Exhaustive Truth Table Test Cases (8 combinations)
        a = 0; b = 0; cin = 0; #10;
        $display("%0t\t%b %b  %b  |  %b    %b", $time, a, b, cin, sum, cout);

        a = 0; b = 0; cin = 1; #10;
        $display("%0t\t%b %b  %b  |  %b    %b", $time, a, b, cin, sum, cout);

        a = 0; b = 1; cin = 0; #10;
        $display("%0t\t%b %b  %b  |  %b    %b", $time, a, b, cin, sum, cout);

        a = 0; b = 1; cin = 1; #10;
        $display("%0t\t%b %b  %b  |  %b    %b", $time, a, b, cin, sum, cout);

        a = 1; b = 0; cin = 0; #10;
        $display("%0t\t%b %b  %b  |  %b    %b", $time, a, b, cin, sum, cout);

        a = 1; b = 0; cin = 1; #10;
        $display("%0t\t%b %b  %b  |  %b    %b", $time, a, b, cin, sum, cout);

        a = 1; b = 1; cin = 0; #10;
        $display("%0t\t%b %b  %b  |  %b    %b", $time, a, b, cin, sum, cout);

        a = 1; b = 1; cin = 1; #10;
        $display("%0t\t%b %b  %b  |  %b    %b", $time, a, b, cin, sum, cout);

        $finish;
    end
endmodule
`endif
