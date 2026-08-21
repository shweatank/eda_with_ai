// ==========================================
// 1. 2-to-4 Decoder
// ==========================================
module decoder_2to4 (
    input  logic [1:0] a,
    output logic [3:0] y
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

// ==========================================
// 2. 2-to-1 Multiplexer (using if-else)
// ==========================================
module mux_if ( 
    input  logic a, 
    input  logic b, 
    input  logic sel, 
    output logic y 
); 
    always_comb begin 
        if (sel == 1'b0) 
            y = a; 
        else 
            y = b; 
    end 
endmodule

// ==========================================
// 3. 8-bit Comparator
// ==========================================
module comparator (
    input  logic [7:0] a,
    input  logic [7:0] b,
    output logic       equal,
    output logic       greater,
    output logic       less
);
    assign equal   = (a == b);
    assign greater = (a > b);
    assign less    = (a < b);
endmodule


// ==========================================
// Testbench Wrapper for Simulation
// ==========================================
`ifndef SYNTHESIS
module tb_combinational;
    // Decoder signals
    logic [1:0] dec_a;
    logic [3:0] dec_y;

    // Mux signals
    logic m_a, m_b, m_sel, m_y;

    // Comparator signals
    logic [7:0] cmp_a, cmp_b;
    logic cmp_eq, cmp_gt, cmp_lt;

    // Instantiate modules
    decoder_2to4 u_dec (.a(dec_a), .y(dec_y));
    mux_if       u_mux (.a(m_a), .b(m_b), .sel(m_sel), .y(m_y));
    comparator   u_cmp (.a(cmp_a), .b(cmp_b), .equal(cmp_eq), .greater(cmp_gt), .less(cmp_lt));

    initial begin
        $dumpfile("combined.vcd");
        $dumpvars(0, tb_combinational);

        $display("=== Testing 2-to-4 Decoder ===");
        dec_a = 2'b00; #10; $display("a=%b -> y=%b", dec_a, dec_y);
        dec_a = 2'b01; #10; $display("a=%b -> y=%b", dec_a, dec_y);
        dec_a = 2'b10; #10; $display("a=%b -> y=%b", dec_a, dec_y);
        dec_a = 2'b11; #10; $display("a=%b -> y=%b", dec_a, dec_y);

        $display("\n=== Testing Mux (if-else) ===");
        m_a = 1'b0; m_b = 1'b1;
        m_sel = 0; #10; $display("sel=%b (a=%b, b=%b) -> y=%b", m_sel, m_a, m_b, m_y);
        m_sel = 1; #10; $display("sel=%b (a=%b, b=%b) -> y=%b", m_sel, m_a, m_b, m_y);

        $display("\n=== Testing 8-bit Comparator ===");
        cmp_a = 8'd45; cmp_b = 8'd20; #10;
        $display("a=%0d, b=%0d -> Equal=%b, Greater=%b, Less=%b", cmp_a, cmp_b, cmp_eq, cmp_gt, cmp_lt);

        cmp_a = 8'd10; cmp_b = 8'd10; #10;
        $display("a=%0d, b=%0d -> Equal=%b, Greater=%b, Less=%b", cmp_a, cmp_b, cmp_eq, cmp_gt, cmp_lt);

        $finish;
    end
endmodule
`endif
