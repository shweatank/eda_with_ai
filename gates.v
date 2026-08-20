module and_gate (input a, input b, output y);
    assign y = a & b;
    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, and_gate);
    end
endmodule

module or_gate (input a, input b, output y);
    assign y = a | b;
    initial begin
        $dumpfile("dump_or.vcd");
        $dumpvars(0, or_gate);
    end
endmodule

module not_gate (input a, output y);
    assign y = ~a;
    initial begin
        $dumpfile("dump_not.vcd");
        $dumpvars(0, not_gate);
    end
endmodule

module xor_gate (input a, input b, output y);
    assign y = a ^ b;
    initial begin
        $dumpfile("dump_xor.vcd");
        $dumpvars(0, xor_gate);
    end
endmodule

module nand_gate (input a, input b, output y);
    assign y = ~(a & b);
    initial begin
        $dumpfile("dump_nand.vcd");
        $dumpvars(0, nand_gate);
    end
endmodule

module nor_gate (input a, input b, output y);
    assign y = ~(a | b);
    initial begin
        $dumpfile("dump_nor.vcd");
        $dumpvars(0, nor_gate);
    end
endmodule

module xnor_gate (input a, input b, output y);
    assign y = ~(a ^ b);
    initial begin
        $dumpfile("dump_xnor.vcd");
        $dumpvars(0, xnor_gate);
    end
endmodule