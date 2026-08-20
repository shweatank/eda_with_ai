// Full Adder built from two half adders + OR gate
module full_adder (
    input  wire a,
    input  wire b,
    input  wire cin,
    output wire sum,
    output wire cout
);
    wire s1, c1, c2;

    half_adder ha1 (.a(a),  .b(b), .sum(s1), .cout(c1));
    half_adder ha2 (.a(s1), .b(cin), .sum(sum), .cout(c2));

    assign cout = c1 | c2;
endmodule

// Half Adder (reused by full_adder)
module half_adder (
    input  wire a,
    input  wire b,
    output wire sum,
    output wire cout
);
    assign sum  = a ^ b;
    assign cout = a & b;
endmodule
