module adder (
    input  wire signed [7:0] a,
    input  wire signed [7:0] b,
    output wire signed [8:0] y   // 5 bits to capture carry-out
);
    // Pure arithmetic addition
    assign y = a + b;

    // Dump waveform for GTKWave
    initial begin
        $dumpfile("adder.vcd");
        $dumpvars(0, adder);
    end
endmodule
