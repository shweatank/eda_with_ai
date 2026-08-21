module mux_3bit (
    input wire [2:0] a,
    input wire [2:0] b,
    input wire sel,
    output wire [2:0] y
);

    assign y = sel ? b : a;

endmodule