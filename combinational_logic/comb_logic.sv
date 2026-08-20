module comb_logic (
    input  wire a,
    input  wire b,
    input  wire c,
    output wire y
);

    assign y = (a & b)|c;
    initial begin
        $dumpfile("comb_logic.vcd");
        $dumpvars(0, comb_logic);
    end	 
endmodule
