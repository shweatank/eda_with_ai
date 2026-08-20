// 4:1 Multiplexer
module mux4to1 (
    input  wire [3:0] d,    // d[0]..d[3] data inputs
    input  wire [1:0] sel,
    output wire        y
);
    assign y = d[sel];
endmodule
