module and_gate (
    input  wire a,
    input  wire b,
    output wire y
);

    assign y = a & b;

endmodule


module or_gate (
    input  logic a,
    input  logic b,
    output logic y
);
    assign y = a | b;
endmodule


module nand_gate (
    input  logic a,
    input logic b,
    output logic y
);
    assign y = ~(a & b);
endmodule


module nor_gate (
    input  logic a,
    input logic b,
    output logic y
);
    assign y = ~(a | b);
endmodule


module xor_gate (
    input  logic a,
    input  logic b,
    output logic y
);
    assign y = a ^ b;
endmodule


module not_gate (
    input  logic a,
    output logic y
);
    assign y = ~a;
endmodule


module all_gates;

    logic a;
    logic b;

    logic and_y;
    logic or_y;
    logic nand_y;
    logic nor_y;
    logic xor_y;
    logic not_y;

    and_gate  u_and  (.a(a), .b(b), .y(and_y));
    or_gate   u_or   (.a(a), .b(b), .y(or_y));
    nand_gate u_nand (.a(a), .b(b), .y(nand_y));
    nor_gate  u_nor  (.a(a), .b(b), .y(nor_y));
    xor_gate  u_xor  (.a(a), .b(b), .y(xor_y));
    not_gate  u_not  (.a(a), .y(not_y));

endmodule