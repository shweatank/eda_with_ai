module vector_gates_combined #(
    parameter WIDTH = 8
)(
    input  wire [WIDTH-1:0] a,
    input  wire [WIDTH-1:0] b,
    input  wire [2:0]       sel,

    // Every gate's result, always available
    output wire [WIDTH-1:0] y_and,
    output wire [WIDTH-1:0] y_or,
    output wire [WIDTH-1:0] y_xor,
    output wire [WIDTH-1:0] y_nand,
    output wire [WIDTH-1:0] y_nor,
    output wire [WIDTH-1:0] y_xnor,
    output wire [WIDTH-1:0] y_not_a,
    output wire [WIDTH-1:0] y_not_b,

    // Whichever single gate `sel` picks, taken from the outputs above
    output reg  [WIDTH-1:0] y_sel
);

    // Gate select encoding (used by y_sel)
    localparam GATE_AND   = 3'd0;
    localparam GATE_OR    = 3'd1;
    localparam GATE_XOR   = 3'd2;
    localparam GATE_NAND  = 3'd3;
    localparam GATE_NOR   = 3'd4;
    localparam GATE_XNOR  = 3'd5;
    localparam GATE_NOT_A = 3'd6;
    localparam GATE_NOT_B = 3'd7;

    genvar i;
    generate
        for (i = 0; i < WIDTH; i = i + 1) begin : GEN_GATES
            assign y_and[i]   = a[i] & b[i];
            assign y_or[i]    = a[i] | b[i];
            assign y_xor[i]   = a[i] ^ b[i];
            assign y_nand[i]  = ~(a[i] & b[i]);
            assign y_nor[i]   = ~(a[i] | b[i]);
            assign y_xnor[i]  = ~(a[i] ^ b[i]);
            assign y_not_a[i] = ~a[i];
            assign y_not_b[i] = ~b[i];
        end
    endgenerate

    // Single selected output, built from the results above (not
    // recomputed) so y_sel always matches whichever y_* it names.
    always @(*) begin
        case (sel)
            GATE_AND:   y_sel = y_and;
            GATE_OR:    y_sel = y_or;
            GATE_XOR:   y_sel = y_xor;
            GATE_NAND:  y_sel = y_nand;
            GATE_NOR:   y_sel = y_nor;
            GATE_XNOR:  y_sel = y_xnor;
            GATE_NOT_A: y_sel = y_not_a;
            GATE_NOT_B: y_sel = y_not_b;
            default:    y_sel = {WIDTH{1'b0}};
        endcase
    end

    initial begin
        $dumpfile("vector_gates_combined.vcd");
        $dumpvars(0, vector_gates_combined);
    end

endmodule