`timescale 1ns/1ps
module waveform_tb;
    reg pclk = 0, presetn = 0, psel = 0, penable = 0, pwrite = 0, uart_rx = 1;
    reg [7:0] paddr = 0; reg [31:0] pwdata = 0;
    wire [31:0] prdata; wire pready, pslverr, uart_tx, irq;
    apb_uart dut(.pclk(pclk),.presetn(presetn),.psel(psel),.penable(penable),.pwrite(pwrite),.paddr(paddr),.pwdata(pwdata),.prdata(prdata),.pready(pready),.pslverr(pslverr),.uart_rx(uart_rx),.uart_tx(uart_tx),.irq(irq));
    always #5 pclk = ~pclk;
    initial begin
        $dumpfile("apb_uart.vcd"); $dumpvars(0, waveform_tb);
        #30 presetn = 1;
        #20 psel = 1; pwrite = 1; paddr = 8'h0C; pwdata = 1; #10 penable = 1; #10 psel = 0; penable = 0;
        #20 psel = 1; pwrite = 1; paddr = 0; pwdata = 8'hA5; #10 penable = 1; #10 psel = 0; penable = 0;
        #400 $finish;
    end
endmodule
