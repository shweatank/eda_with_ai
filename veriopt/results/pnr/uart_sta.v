module uart (clk,
    data_in,
    data_out,
    rst,
    VSS,
    VDD);
 input clk;
 input data_in;
 output data_out;
 input rst;
 inout VSS;
 inout VDD;

 wire _0_;

 sky130_fd_sc_hd__inv_1 _1_ (.A(rst),
    .Y(_0_));
 sky130_fd_sc_hd__dfrtp_2 _2_ (.D(data_in),
    .Q(data_out),
    .RESET_B(_0_),
    .CLK(clk));
endmodule
