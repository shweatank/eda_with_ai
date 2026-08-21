// ==========================================
// 4-to-2 Binary Encoder
// ==========================================
module encoder_4to2 (
    input  logic [3:0] a, // 4-bit active-high inputs (one-hot encoded)
    output logic [1:0] y, // 2-bit binary output
    output logic       v  // Valid flag (1 if at least one input is active)
);

    always_comb begin
        y = 2'b00;
        v = 1'b1;
        case (a)
            4'b0001: y = 2'b00;
            4'b0010: y = 2'b01;
            4'b0100: y = 2'b10;
            4'b1000: y = 2'b11;
            default: begin
                y = 2'b00;
                v = 1'b0; // Invalid / no active input
            end
        endcase
    end
endmodule

// Simulation testbench wrapper
`ifndef SYNTHESIS
module tb_encoder;
    logic [3:0] a;
    logic [1:0] y;
    logic       v;

    encoder_4to2 uut (.a(a), .y(y), .v(v));

    initial begin
        $dumpfile("encoder.vcd");
        $dumpvars(0, tb_encoder);

        // Test active-high input: input line 2 is high (0100)
        a = 4'b0100; #10;
        $display("RESULT:%b,%b,%b", a, y, v);
        $finish;
    end
endmodule
`endif
