// File: files_mux4/mux4.sv
module mux4 (
    input  logic [3:0] d,   // 4 individual data inputs
    input  logic [1:0] sel, // 2-bit select line
    output logic       y    // Output selected data
);

    always_comb begin
        case (sel)
            2'b00:   y = d[0];
            2'b01:   y = d[1];
            2'b10:   y = d[2];
            2'b11:   y = d[3];
            default: y = 1'b0; 
        endcase
    end
endmodule

`ifndef SYNTHESIS
module tb_mux4;
    logic [3:0] d;
    logic [1:0] sel;
    logic       y;

    mux4 uut (.*);

    initial begin
        $dumpfile("mux4.vcd");
        $dumpvars(0, tb_mux4);
        
        $display("Time | d[3:0] | sel | y");
        $display("-----------------------");

        d = 4'b1010; 
        sel = 2'b00; #10; $display("%0t |  %b  |  %b  | %b", $time, d, sel, y);
        sel = 2'b01; #10; $display("%0t |  %b  |  %b  | %b", $time, d, sel, y);
        sel = 2'b10; #10; $display("%0t |  %b  |  %b  | %b", $time, d, sel, y);
        sel = 2'b11; #10; $display("%0t |  %b  |  %b  | %b", $time, d, sel, y);
        $finish;
    end
endmodule
`endif
