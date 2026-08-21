module mux_if (
    input  wire a,
    input  wire b,
    input  wire sel,
    output reg  y
);
    always @(*) begin
        if (sel == 1'b0)
            y = a;
        else
            y = b;
    end

    initial begin
        $dumpfile("mux_if.vcd");
        $dumpvars(0, mux_if);
    end
endmodule
