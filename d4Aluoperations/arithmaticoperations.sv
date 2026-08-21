// Combined ALU: addition, subtraction, multiplication, division
// Each operation has an unsigned and a signed 8-bit variant.
// alu_top instantiates all eight so everything can be simulated/
// synthesized together under one top module.

// ---------------- Addition ----------------
module adder_unsigned (
    input  wire [7:0] A,
    input  wire [7:0] B,
    output wire [7:0] y
);
    assign y = A + B;
endmodule

module adder_signed (
    input  wire signed [7:0] A,
    input  wire signed [7:0] B,
    output wire signed [7:0] y
);
    assign y = A + B;
endmodule

// ---------------- Subtraction ----------------
module subtractor_unsigned (
    input  wire [7:0] A,
    input  wire [7:0] B,
    output wire [7:0] y
);
    assign y = A - B;
endmodule

module subtractor_signed (
    input  wire signed [7:0] A,
    input  wire signed [7:0] B,
    output wire signed [7:0] y
);
    assign y = A - B;
endmodule

// ---------------- Multiplication ----------------
// Product width is double the input width (16 bits) to avoid overflow.
module multiplier_unsigned (
    input  wire [7:0]  A,
    input  wire [7:0]  B,
    output wire [15:0] product
);
    assign product = A * B;
endmodule

module multiplier_signed (
    input  wire signed [7:0]  A,
    input  wire signed [7:0]  B,
    output wire signed [15:0] product
);
    assign product = A * B;
endmodule

// ---------------- Division ----------------
// Guarded against divide-by-zero (forces output to 0 instead of X).
module divider_unsigned (
    input  wire [7:0] A,
    input  wire [7:0] B,
    output wire [7:0] quotient,
    output wire [7:0] remainder
);
    assign quotient  = (B != 0) ? (A / B) : 8'd0;
    assign remainder = (B != 0) ? (A % B) : 8'd0;
endmodule

module divider_signed (
    input  wire signed [7:0] A,
    input  wire signed [7:0] B,
    output wire signed [7:0] quotient,
    output wire signed [7:0] remainder
);
    assign quotient  = (B != 0) ? (A / B) : 8'sd0;
    assign remainder = (B != 0) ? (A % B) : 8'sd0;
endmodule

// ---------------- Combined ALU top ----------------
module alu_top (
    // Addition
    input  wir// Combined ALU: addition, subtraction, multiplication, division
// Each operation has an unsigned and a signed 8-bit variant.
// alu_top instantiates all eight so everything can be simulated/
// synthesized together under one top module.

// ---------------- Addition ----------------
module adder_unsigned (
    input  wire [7:0] A,
    input  wire [7:0] B,
    output wire [7:0] y
);
    assign y = A + B;
endmodule

module adder_signed (
    input  wire signed [7:0] A,
    input  wire signed [7:0] B,
    output wire signed [7:0] y
);
    assign y = A + B;
endmodule

// ---------------- Subtraction ----------------
module subtractor_unsigned (
    input  wire [7:0] A,
    input  wire [7:0] B,
    output wire [7:0] y
);
    assign y = A - B;
endmodule

module subtractor_signed (
    input  wire signed [7:0] A,
    input  wire signed [7:0] B,
    output wire signed [7:0] y
);
    assign y = A - B;
endmodule

// ---------------- Multiplication ----------------
// Product width is double the input width (16 bits) to avoid overflow.
module multiplier_unsigned (
    input  wire [7:0]  A,
    input  wire [7:0]  B,
    output wire [15:0] product
);
    assign product = A * B;
endmodule

module multiplier_signed (
    input  wire signed [7:0]  A,
    input  wire signed [7:0]  B,
    output wire signed [15:0] product
);
    assign product = A * B;
endmodule

// ---------------- Division ----------------
// Guarded against divide-by-zero (forces output to 0 instead of X).
module divider_unsigned (
    input  wire [7:0] A,
    input  wire [7:0] B,
    output wire [7:0] quotient,
    output wire [7:0] remainder
);
    assign quotient  = (B != 0) ? (A / B) : 8'd0;
    assign remainder = (B != 0) ? (A % B) : 8'd0;
endmodule

module divider_signed (
    input  wire signed [7:0] A,
    input  wire signed [7:0] B,
    output wire signed [7:0] quotient,
    output wire signed [7:0] remainder
);
    assign quotient  = (B != 0) ? (A / B) : 8'sd0;
    assign remainder = (B != 0) ? (A % B) : 8'sd0;
endmodule

// ---------------- Combined ALU top ----------------
module alu_top (
    // Addition
    input  wire [7:0]        Add_A_u,
    input  wire [7:0]        Add_B_u,
    output wire [7:0]        Add_Y_u,
    input  wire signed [7:0] Add_A_s,
    input  wire signed [7:0] Add_B_s,
    output wire signed [7:0] Add_Y_s,

    // Subtraction
    input  wire [7:0]        Sub_A_u,
    input  wire [7:0]        Sub_B_u,
    output wire [7:0]        Sub_Y_u,
    input  wire signed [7:0] Sub_A_s,
    input  wire signed [7:0] Sub_B_s,
    output wire signed [7:0] Sub_Y_s,

    // Multiplication
    input  wire [7:0]         Mul_A_u,
    input  wire [7:0]         Mul_B_u,
    output wire [15:0]        Mul_Y_u,
    input  wire signed [7:0]  Mul_A_s,
    input  wire signed [7:0]  Mul_B_s,
    output wire signed [15:0] Mul_Y_s,

    // Division
    input  wire [7:0]        Div_A_u,
    input  wire [7:0]        Div_B_u,
    output wire [7:0]        Div_Q_u,
    output wire [7:0]        Div_R_u,
    input  wire signed [7:0] Div_A_s,
    input  wire signed [7:0] Div_B_s,
    output wire signed [7:0] Div_Q_s,
    output wire signed [7:0] Div_R_s
);
    adder_unsigned u_add_u (.A(Add_A_u), .B(Add_B_u), .y(Add_Y_u));
    adder_signed   u_add_s (.A(Add_A_s), .B(Add_B_s), .y(Add_Y_s));

    subtractor_unsigned u_sub_u (.A(Sub_A_u), .B(Sub_B_u), .y(Sub_Y_u));
    subtractor_signed   u_sub_s (.A(Sub_A_s), .B(Sub_B_s), .y(Sub_Y_s));

    multiplier_unsigned u_mul_u (.A(Mul_A_u), .B(Mul_B_u), .product(Mul_Y_u));
    multiplier_signed   u_mul_s (.A(Mul_A_s), .B(Mul_B_s), .product(Mul_Y_s));

    divider_unsigned u_div_u (.A(Div_A_u), .B(Div_B_u), .quotient(Div_Q_u), .remainder(Div_R_u));
    divider_signed   u_div_s (.A(Div_A_s), .B(Div_B_s), .quotient(Div_Q_s), .remainder(Div_R_s));

    initial begin
        $dumpfile("alu_top.vcd");
        $dumpvars(0, alu_top);
    end
endmodulee [7:0]        Add_A_u,
    input  wire [7:0]        Add_B_u,
    output wire [7:0]        Add_Y_u,
    input  wire signed [7:0] Add_A_s,
    input  wire signed [7:0] Add_B_s,
    output wire signed [7:0] Add_Y_s,

    // Subtraction
    input  wire [7:0]        Sub_A_u,
    input  wire [7:0]        Sub_B_u,
    output wire [7:0]        Sub_Y_u,
    input  wire signed [7:0] Sub_A_s,
    input  wire signed [7:0] Sub_B_s,
    output wire signed [7:0] Sub_Y_s,

    // Multiplication
    input  wire [7:0]         Mul_A_u,
    input  wire [7:0]         Mul_B_u,
    output wire [15:0]        Mul_Y_u,
    input  wire signed [7:0]  Mul_A_s,
    input  wire signed [7:0]  Mul_B_s,
    output wire signed [15:0] Mul_Y_s,

    // Division
    input  wire [7:0]        Div_A_u,
    input  wire [7:0]        Div_B_u,
    output wire [7:0]        Div_Q_u,
    output wire [7:0]        Div_R_u,
    input  wire signed [7:0] Div_A_s,
    input  wire signed [7:0] Div_B_s,
    output wire signed [7:0] Div_Q_s,
    output wire signed [7:0] Div_R_s
);
    adder_unsigned u_add_u (.A(Add_A_u), .B(Add_B_u), .y(Add_Y_u));
    adder_signed   u_add_s (.A(Add_A_s), .B(Add_B_s), .y(Add_Y_s));

    subtractor_unsigned u_sub_u (.A(Sub_A_u), .B(Sub_B_u), .y(Sub_Y_u));
    subtractor_signed   u_sub_s (.A(Sub_A_s), .B(Sub_B_s), .y(Sub_Y_s));

    multiplier_unsigned u_mul_u (.A(Mul_A_u), .B(Mul_B_u), .product(Mul_Y_u));
    multiplier_signed   u_mul_s (.A(Mul_A_s), .B(Mul_B_s), .product(Mul_Y_s));

    divider_unsigned u_div_u (.A(Div_A_u), .B(Div_B_u), .quotient(Div_Q_u), .remainder(Div_R_u));
    divider_signed   u_div_s (.A(Div_A_s), .B(Div_B_s), .quotient(Div_Q_s), .remainder(Div_R_s));

    initial begin
        $dumpfile("alu_top.vcd");
        $dumpvars(0, alu_top);
    end
endmodule