module ALU (
    input  logic [3:0] a,
    input  logic [3:0] b,
    input  logic [1:0] op,

    output logic [7:0] result
);

    logic [4:0] add_result;
    logic [3:0] sub_result;
    logic [7:0] mul_result;
    logic [3:0] div_result;

    // ADDER
   four_bit_ALU u_adder (
        .a(a),
        .b(b),
        .sum(add_result)
    );

    // SUBTRACTOR
    four_bit_sub u_sub (
        .a(a),
        .b(b),
        .diff(sub_result)
    );

    // MULTIPLIER
    multiplier u_mul (
        .a(a),
        .b(b),
        .res(mul_result)
    );

    // DIVIDER
    divider u_div (
        .a(a),
        .b(b),
        .res(div_result)
    );

    // OPERATION SELECT
    always_comb begin

        case (op)

            2'b00: result = {3'b000, add_result};

            2'b01: result = {4'b0000, sub_result};

            2'b10: result = mul_result;

            2'b11: result = {4'b0000, div_result};

            default: result = 8'b0;

        endcase

    end

endmodule
