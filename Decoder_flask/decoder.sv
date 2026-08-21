// ==========================================
// 2-to-4 Decoder
// ==========================================
module decoder_2to4 (
    input  logic [1:0] a, // 2-bit binary input
    output logic [3:0] y  // 4-bit active-high one-hot outputs
);

    always_comb begin
        case (a)
            2'b00:   y = 4'b0001;
            2'b01:   y = 4'b0010;
            2'b10:   y = 4'b0100;
            2'b11:   y = 4'b1000;
            default: y = 4'b0000;
        endcase
    end
endmodule

// Simulation testbench wrapper
`ifndef SYNTHESIS
module tb_decoder;
    logic [1:0] a;
    logic [3:0] y;

    decoder_2to4 uut (.a(a), .y(y));

    initial begin
        $dumpfile("decoder.vcd");
        $dumpvars(0, tb_decoder);

        // Test input binary value: 2 (binary 10)
        a = 2'b10; #10;
        $display("RESULT:%b,%b", a, y);
        $finish;
    end
endmodule
`endif
