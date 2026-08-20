module combo_logic (
    input  wire a,
    input  wire b,
    input  wire c,
    output wire y
);

    // Logic implementation: y = (a & b) | c
    assign y = (a & b) | c;

    // Generate VCD file for GTKWave visualization
    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, combo_logic);
    end

endmodule