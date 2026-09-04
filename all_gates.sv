// AND gate
module and_gate (
    input  wire a,
    input  wire b,
    output wire y
);
    assign y = a & b;
    initial begin
        $dumpfile("and_gate.vcd");
        $dumpvars(0, and_gate);
    end
endmodule

// NAND gate
module nand_gate (
    input  wire a,
    input  wire b,
    output wire y
);
    assign y = ~(a & b);
    initial begin
        $dumpfile("nand_gate.vcd");
        $dumpvars(0, nand_gate);
    end
endmodule

// NOR gate
module nor_gate (
    input  wire a,
    input  wire b,
    output wire y
);
    assign y = ~(a | b);
    initial begin
        $dumpfile("nor_gate.vcd");
        $dumpvars(0, nor_gate);
    end
endmodule

// NOT gate
module not_gate (
    input  wire a,
    output wire y
);
    assign y = ~a;
    initial begin
        $dumpfile("not_gate.vcd");
        $dumpvars(0, not_gate);
    end
endmodule

// OR gate
module or_gate (
    input  wire a,
    input  wire b,
    output wire y
);
    assign y = a | b;
    initial begin
        $dumpfile("or_gate.vcd");
        $dumpvars(0, or_gate);
    end
endmodule

// XOR gate
module xor_gate (
    input  wire a,
    input  wire b,
    output wire y
);
    assign y = a ^ b;
    initial begin
        $dumpfile("xor_gate.vcd");
        $dumpvars(0, xor_gate);
    end
endmodule

// Wrapper module combining all gates
module all_gates (
    input  wire a,
    input  wire b,
    output wire y_and,
    output wire y_nand,
    output wire y_nor,
    output wire y_not,
    output wire y_or,
    output wire y_xor
);
    and_gate  u_and  (.a(a), .b(b), .y(y_and));
    nand_gate u_nand (.a(a), .b(b), .y(y_nand));
    nor_gate  u_nor  (.a(a), .b(b), .y(y_nor));
    not_gate  u_not  (.a(a), .y(y_not));
    or_gate   u_or   (.a(a), .b(b), .y(y_or));
    xor_gate  u_xor  (.a(a), .b(b), .y(y_xor));
endmodule