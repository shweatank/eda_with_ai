// File: files_multiplier/multiplier.sv
module multiplier #(parameter WIDTH = 4) (
    input  logic [WIDTH-1:0] a,
    input  logic [WIDTH-1:0] b,
    input  logic             is_signed, // 0 for Unsigned, 1 for Signed multiplication
    output logic [2*WIDTH-1:0] product,   // Full double-width product
    output logic             overflow   // Overflow flag if upper bits are utilized/invalid
);

    // Internal wires for signed and unsigned results
    logic [2*WIDTH-1:0] unsigned_prod;
    logic [2*WIDTH-1:0] signed_prod;

    // Unsigned multiplication
    assign unsigned_prod = a * b;

    // Signed multiplication (casting inputs to signed types)
    assign signed_prod = $signed(a) * $signed(b);

    // Select product based on mode
    assign product = is_signed ? signed_prod : unsigned_prod;

    // Overflow detection: 
    // For unsigned, overflow occurs if any bits in the upper half [2*WIDTH-1 : WIDTH] are non-zero 
    // (assuming we want to check if it fits back into WIDTH, though multipliers normally output 2*WIDTH).
    // For signed, overflow occurs if the result exceeds the single-WIDTH signed range.
    always_comb begin
        if (is_signed) begin
            // Check if upper half contains bits other than sign extensions
            overflow = (product[2*WIDTH-1:WIDTH] != {WIDTH{product[WIDTH-1]}});
        end else begin
            // Check if any bit in the upper half is 1
            overflow = (product[2*WIDTH-1:WIDTH] != '0);
        end
    end

endmodule

// Simulation testbench wrapper (Automatically ignored by Yosys during synthesis)
`ifndef SYNTHESIS
module tb_multiplier;
    parameter WIDTH = 4;
    logic [WIDTH-1:0] a, b;
    logic             is_signed;
    logic [2*WIDTH-1:0] product;
    logic             overflow;

    multiplier #(.WIDTH(WIDTH)) uut (
        .a(a), .b(b), .is_signed(is_signed),
        .product(product), .overflow(overflow)
    );

    initial begin
        $dumpfile("multiplier.vcd");
        $dumpvars(0, tb_multiplier);

        $display("Time\ta    b    signed? | product   overflow");
        $display("----------------------------------------");

        // Test 1: Unsigned Normal (3 * 2 = 6)
        a = 4'b0011; b = 4'b0010; is_signed = 0; #10;
        $display("%0t\t%b  %b    %b       | %b   %b", $time, a, b, is_signed, product, overflow);

        // Test 2: Unsigned Overflow check (15 * 2 = 30 -> exceeds 4-bit bounds)
        a = 4'b1111; b = 4'b0010; is_signed = 0; #10;
        $display("%0t\t%b  %b    %b       | %b   %b", $time, a, b, is_signed, product, overflow);

        // Test 3: Signed Normal (-3 * 2 = -6) -> (-3 is 1101 in 4-bit two's complement)
        a = 4'b1101; b = 4'b0010; is_signed = 1; #10;
        $display("%0t\t%b  %b    %b       | %b   %b", $time, a, b, is_signed, product, overflow);

        $finish;
    end
endmodule
`endif
