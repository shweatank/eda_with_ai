`timescale 1ns/1ps

module waveform_tb;
    reg [7:0] a = 0;
    reg [7:0] b = 0;
    wire [7:0] y;

    vector_and #(.WIDTH(8)) dut (
        .a(a),
        .b(b),
        .y(y)
    );

    initial begin
        $dumpfile("vector_and.vcd");
        $dumpvars(0, waveform_tb);

        #10 a = 8'hFF; b = 8'h00;
        #10 a = 8'hFF; b = 8'hFF;
        #10 a = 8'hAA; b = 8'h55;
        #10 a = 8'h0F; b = 8'hF0;
        #10 a = 8'h3C; b = 8'hA5;
        #10 $finish;
    end
endmodule
