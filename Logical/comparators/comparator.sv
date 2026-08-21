module comparator (
    input wire [7:0] a,
    input wire [7:0] b,

    output wire equal,
    output wire greater,
    output wire less
);

    assign equal   = (a == b);
    assign greater = (a > b);
    assign less    = (a < b);

endmodule
