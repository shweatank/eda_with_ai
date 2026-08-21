module alu #(parameter WIDTH = 4) (
    input  logic [WIDTH-1:0] a,
    input  logic [WIDTH-1:0] b,
    input  logic             cin,       
    input  logic             is_signed, 
    input  logic [2:0]       opcode,    
    output logic [2*WIDTH-1:0] result,  
    output logic             cout_bout, 
    output logic             overflow,  
    output logic             div_by_zero
);

    localparam OP_ADD = 3'b001; 
    localparam OP_SUB = 3'b010; 
    localparam OP_MUL = 3'b011; 
    localparam OP_DIV = 3'b100; 

    logic [WIDTH:0]     add_ext, sub_ext;
    logic [2*WIDTH-1:0] mul_unsigned, mul_signed;
    logic [WIDTH-1:0]   div_q, div_r;

    assign add_ext = {1'b0, a} + {1'b0, b} + cin;
    assign sub_ext = {1'b1, a} - {1'b0, b} - {{(WIDTH){1'b0}}, cin};
    assign mul_unsigned = a * b;
    assign mul_signed   = $signed(a) * $signed(b);
    assign div_by_zero = (b == '0);
    assign div_q       = div_by_zero ? {WIDTH{1'b1}} : (a / b);
    assign div_r       = div_by_zero ? a             : (a % b);

    always_comb begin
        result    = '0;
        cout_bout = 1'b0;
        overflow  = 1'b0;

        case (opcode)
            OP_ADD: begin
                result[WIDTH-1:0] = add_ext[WIDTH-1:0];
                cout_bout         = add_ext[WIDTH];
                overflow          = (a[WIDTH-1] == b[WIDTH-1]) && (result[WIDTH-1] != a[WIDTH-1]);
            end
            OP_SUB: begin
                result[WIDTH-1:0] = sub_ext[WIDTH-1:0];
                cout_bout         = ~sub_ext[WIDTH]; 
                overflow          = (a[WIDTH-1] != b[WIDTH-1]) && (result[WIDTH-1] == b[WIDTH-1]);
            end
            OP_MUL: begin
                result = is_signed ? mul_signed : mul_unsigned;
                overflow = is_signed ? (result[2*WIDTH-1:WIDTH] != {WIDTH{result[WIDTH-1]}}) : (result[2*WIDTH-1:WIDTH] != '0);
            end
            OP_DIV: begin
                result[WIDTH-1:0]   = div_q;
                result[2*WIDTH-1:WIDTH] = div_r; 
            end
            default: result = '0;
        endcase
    end
endmodule

`ifndef SYNTHESIS
module tb_alu;
    parameter WIDTH = 4;
    logic [WIDTH-1:0] a, b;
    logic             cin, is_signed;
    logic [2:0]       opcode;
    logic [2*WIDTH-1:0] result;
    logic             cout_bout, overflow, div_by_zero;

    alu #(.WIDTH(WIDTH)) uut (.*);

    initial begin
        $dumpfile("alu.vcd");
        $dumpvars(0, tb_alu);
        
        // Dynamic Test Vectors (can be overridden or customized via file/args if needed, 
        // for now simulating a signed addition overflow: 7 + 1)
        a = 4'b0111; b = 4'b0001; cin = 0; is_signed = 1; opcode = 3'b001; #10;
        $display("VALS:%b,%b,%b,%b,%b,%b,%b,%b,%b", a, b, cin, is_signed, opcode, result[WIDTH-1:0], cout_bout, overflow, div_by_zero);
        $finish;
    end
endmodule
`endif
