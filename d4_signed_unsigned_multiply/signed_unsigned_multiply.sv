// Combined multiplier: instantiates both unsigned and signed 8x8 -> 16 multipliers
// so both can be simulated/synthesized together under one top module.
//
// NOTE: product width is double the input width (16 bits for 8-bit inputs).
// Two 8-bit numbers can produce a result that doesn't fit in 8 bits
// (e.g. 255 x 255 = 65025), so truncating to 8 bits would silently
// wrap/overflow far more aggressively than addition ever would.

module multiplier_unsigned (
    input  wire [7:0]  A,
    input  wire [7:0]  B,
    output wire [15:0] product
);
    assign product = A * B;

    initial begin
        $dumpfile("multiplier_unsigned.vcd");
        $dumpvars(0, multiplier_unsigned);
    end
endmodule

module multiplier_signed (
    input  wire signed [7:0]  A,
    input  wire signed [7:0]  B,
    output wire signed [15:0] product
);
    assign product = A * B;

    initial begin
        $dumpfile("multiplier_signed.vcd");
        $dumpvars(0, multiplier_signed);
    end
endmodule

module multiplier_top (
    input  wire [7:0]         A_u,
    input  wire [7:0]         B_u,
    output wire [15:0]        product_u,

    input  wire signed [7:0]  A_s,
    input  wire signed [7:0]  B_s,
    output wire signed [15:0] product_s
);
    multiplier_unsigned u_mul_unsigned (
        .A(A_u),
        .B(B_u),
        .product(product_u)
    );

    multiplier_signed u_mul_signed (
        .A(A_s),
        .B(B_s),
        .product(product_s)
    );

    initial begin
        $dumpfile("multiplier_top.vcd");
        $dumpvars(0, multiplier_top);
    end
endmodule