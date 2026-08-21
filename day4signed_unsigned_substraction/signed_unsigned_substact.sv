// Combined subtractor: instantiates both unsigned and signed 8-bit subtractors
// so both can be simulated/synthesized together under one top module.
//
// NOTE: unlike multiplication, subtraction keeps the same width as the inputs
// (8 bits). This means it CAN overflow/underflow and wrap around, exactly
// like addition does -- there is no extra bit to catch a borrow or carry.

module subtractor_unsigned (
    input  wire [7:0] A,
    input  wire [7:0] B,
    output wire [7:0] y
);
    assign y = A - B;

    initial begin
        $dumpfile("subtractor_unsigned.vcd");
        $dumpvars(0, subtractor_unsigned);
    end
endmodule

module subtractor_signed (
    input  wire signed [7:0] A,
    input  wire signed [7:0] B,
    output wire signed [7:0] y
);
    assign y = A - B;

    initial begin
        $dumpfile("subtractor_signed.vcd");
        $dumpvars(0, subtractor_signed);
    end
endmodule

module subtractor_top (
    input  wire [7:0]        A_u,
    input  wire [7:0]        B_u,
    output wire [7:0]        y_u,

    input  wire signed [7:0] A_s,
    input  wire signed [7:0] B_s,
    output wire signed [7:0] y_s
);
    subtractor_unsigned u_sub_unsigned (
        .A(A_u),
        .B(B_u),
        .y(y_u)
    );

    subtractor_signed u_sub_signed (
        .A(A_s),
        .B(B_s),
        .y(y_s)
    );

    initial begin
        $dumpfile("subtractor_top.vcd");
        $dumpvars(0, subtractor_top);
    end
endmodule