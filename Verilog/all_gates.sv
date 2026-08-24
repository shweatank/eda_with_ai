module and_gate (
    input  a,
    input  b,
    output y
);

assign y = a & b;

initial begin
    $dumpfile("dump.vcd");
    $dumpvars(0, and_gate);
end

endmodule

module nand_gate (
    input  a,
    input  b,
    output y
);

assign y = ~(a & b);

initial begin
    $dumpfile("dump.vcd");
    $dumpvars(0, nand_gate);
end

endmodule

module not_gate (
    input  a,
    output y
);

assign y = ~a;

initial begin
    $dumpfile("dump.vcd");
    $dumpvars(0, not_gate);
end

endmodule

module or_gate (
    input  a,
    input  b,
    output y
);

assign y = a | b;

initial begin
    $dumpfile("dump.vcd");
    $dumpvars(0, or_gate);
end

endmodule

module xor_gate (
    input  a,
    input  b,
    output y
);

assign y = a ^ b;

initial begin
    $dumpfile("dump.vcd");
    $dumpvars(0, xor_gate);
end

endmodule

module all_gates (
    input  and_a,
    input  and_b,
    output and_y,
    input  nand_a,
    input  nand_b,
    output nand_y,
    input  not_a,
    output not_y,
    input  or_a,
    input  or_b,
    output or_y,
    input  xor_a,
    input  xor_b,
    output xor_y
);

and_gate and_instance (
    .a(and_a),
    .b(and_b),
    .y(and_y)
);

nand_gate nand_instance (
    .a(nand_a),
    .b(nand_b),
    .y(nand_y)
);

not_gate not_instance (
    .a(not_a),
    .y(not_y)
);

or_gate or_instance (
    .a(or_a),
    .b(or_b),
    .y(or_y)
);

xor_gate xor_instance (
    .a(xor_a),
    .b(xor_b),
    .y(xor_y)
);

endmodule