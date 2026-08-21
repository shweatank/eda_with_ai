// Combined divider: instantiates both unsigned and signed 8-bit dividers
// so both can be simulated/synthesized together under one top module.

module divider_unsigned (
    input  wire [7:0] A,
    input  wire [7:0] B,
    output wire [7:0] quotient,
    output wire [7:0] remainder
);
    assign quotient  = (B != 0) ? (A / B) : 8'd0;
    assign remainder = (B != 0) ? (A % B) : 8'd0;

    initial begin
        $dumpfile("divider_unsigned.vcd");
        $dumpvars(0, divider_unsigned);
    end
endmodule

module divider_signed (
    input  wire signed [7:0] A,
    input  wire signed [7:0] B,
    output wire signed [7:0] quotient,
    output wire signed [7:0] remainder
);
    assign quotient  = (B != 0) ? (A / B) : 8'sd0;
    assign remainder = (B != 0) ? (A % B) : 8'sd0;

    initial begin
        $dumpfile("divider_signed.vcd");
        $dumpvars(0, divider_signed);
    end
endmodule

module divider_top (
    input  wire [7:0]        A_u,
    input  wire [7:0]        B_u,
    output wire [7:0]        quotient_u,
    output wire [7:0]        remainder_u,

    input  wire signed [7:0] A_s,
    input  wire signed [7:0] B_s,
    output wire signed [7:0] quotient_s,
    output wire signed [7:0] remainder_s
);
    divider_unsigned u_div_unsigned (
        .A(A_u),
        .B(B_u),
        .quotient(quotient_u),
        .remainder(remainder_u)
    );

    divider_signed u_div_signed (
        .A(A_s),
        .B(B_s),
        .quotient(quotient_s),
        .remainder(remainder_s)
    );

    initial begin
        $dumpfile("divider_top.vcd");
        $dumpvars(0, divider_top);
    end
endmodule