`timescale 1ns/1ps

module waveform_tb;
    reg [7:0] a = 0;
    reg [7:0] b = 0;
    reg [7:0] c = 0;
        wire [7:0] y;

    combined_gates #(.WIDTH(8)) dut (
            .a(a), .b(b), .c(c), .y(y)
    );

    initial begin
        $dumpfile("combined_gates.vcd");
        $dumpvars(0, waveform_tb);
        #10 begin a = 8'hFF; b = 8'h00; c = 8'hAA; end
        #10 begin a = 8'hFF; b = 8'hFF; c = 8'h55; end
        #10 begin a = 8'hAA; b = 8'h55; c = 8'h0F; end
        #10 begin a = 8'h0F; b = 8'hF0; c = 8'hF0; end
        #10 begin a = 8'h3C; b = 8'hA5; c = 8'hC3; end
        #10 $finish;
    end
endmodule
