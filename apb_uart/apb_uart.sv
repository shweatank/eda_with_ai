module apb_uart #(
    parameter DATA_WIDTH = 8,
    parameter FIFO_DEPTH = 4
)(
    input  wire        pclk,
    input  wire        presetn,
    input  wire        psel,
    input  wire        penable,
    input  wire        pwrite,
    input  wire [7:0]  paddr,
    input  wire [31:0] pwdata,
    output wire [31:0] prdata,
    output wire        pready,
    output wire        pslverr,
    input  wire        uart_rx,
    output reg         uart_tx,
    output wire        irq
);
    localparam BAUD_DIV = 16;
    localparam PTR_WIDTH = (FIFO_DEPTH <= 2) ? 1 : $clog2(FIFO_DEPTH);
    localparam COUNT_WIDTH = $clog2(FIFO_DEPTH + 1);
    localparam TX_ADDR = 8'h00;
    localparam RX_ADDR = 8'h04;
    localparam STATUS_ADDR = 8'h08;
    localparam CONTROL_ADDR = 8'h0C;

    reg [7:0] tx_fifo [0:FIFO_DEPTH-1];
    reg [7:0] rx_fifo [0:FIFO_DEPTH-1];
    reg [PTR_WIDTH-1:0] tx_wr_ptr, tx_rd_ptr, rx_wr_ptr, rx_rd_ptr;
    reg [COUNT_WIDTH-1:0] tx_count, rx_count;
    reg rx_overrun, framing_error, irq_enable;
    reg [3:0] tx_bit_index, rx_bit_index;
    reg [7:0] tx_shift, rx_shift;
    reg [4:0] tx_baud_count, rx_baud_count;
    reg tx_active, rx_active;

    wire apb_access = psel && penable;
    wire apb_write = apb_access && pwrite;
    wire apb_read = apb_access && !pwrite;
    wire tx_full = (tx_count == FIFO_DEPTH);
    wire tx_empty = (tx_count == 0);
    wire rx_full = (rx_count == FIFO_DEPTH);
    wire rx_empty = (rx_count == 0);

    assign pready = 1'b1;
    assign pslverr = apb_access && ((paddr != TX_ADDR) && (paddr != RX_ADDR) && (paddr != STATUS_ADDR) && (paddr != CONTROL_ADDR));
    assign irq = irq_enable && (!rx_empty || rx_overrun || framing_error);

    assign prdata = (paddr == RX_ADDR) ? {24'b0, rx_empty ? 8'b0 : rx_fifo[rx_rd_ptr]} :
                    (paddr == STATUS_ADDR) ? {25'b0, framing_error, rx_overrun, rx_full, rx_empty, tx_full, tx_empty} :
                    (paddr == CONTROL_ADDR) ? {31'b0, irq_enable} : 32'b0;

    always @(posedge pclk or negedge presetn) begin
        if (!presetn) begin
            tx_wr_ptr <= 0; tx_rd_ptr <= 0; rx_wr_ptr <= 0; rx_rd_ptr <= 0;
            tx_count <= 0; rx_count <= 0; rx_overrun <= 0; framing_error <= 0;
            irq_enable <= 0; uart_tx <= 1; tx_active <= 0; rx_active <= 0;
            tx_bit_index <= 0; rx_bit_index <= 0; tx_baud_count <= 0; rx_baud_count <= 0;
            tx_shift <= 0; rx_shift <= 0;
        end else begin
            if (apb_write && paddr == CONTROL_ADDR) irq_enable <= pwdata[0];
            if (apb_write && paddr == TX_ADDR && !tx_full) begin
                tx_fifo[tx_wr_ptr] <= pwdata[7:0];
                tx_wr_ptr <= (tx_wr_ptr == FIFO_DEPTH - 1) ? 0 : tx_wr_ptr + 1'b1;
                tx_count <= tx_count + 1'b1;
            end
            if (apb_read && paddr == RX_ADDR && !rx_empty) begin
                rx_rd_ptr <= (rx_rd_ptr == FIFO_DEPTH - 1) ? 0 : rx_rd_ptr + 1'b1;
                rx_count <= rx_count - 1'b1;
                rx_overrun <= 0; framing_error <= 0;
            end
            if (!tx_active && !tx_empty) begin
                tx_shift <= tx_fifo[tx_rd_ptr];
                tx_rd_ptr <= (tx_rd_ptr == FIFO_DEPTH - 1) ? 0 : tx_rd_ptr + 1'b1;
                tx_count <= tx_count - 1'b1;
                tx_active <= 1;
                tx_bit_index <= 0;
                tx_baud_count <= 0;
                uart_tx <= 0;
            end else if (tx_active) begin
                if (tx_baud_count == BAUD_DIV - 1) begin
                    tx_baud_count <= 0;
                    tx_bit_index <= tx_bit_index + 1'b1;
                    if (tx_bit_index < 8) uart_tx <= tx_shift[tx_bit_index];
                    else if (tx_bit_index == 8) uart_tx <= 1;
                    else begin uart_tx <= 1; tx_active <= 0; end
                end else tx_baud_count <= tx_baud_count + 1'b1;
            end
            if (!rx_active && !uart_rx) begin
                rx_active <= 1; rx_bit_index <= 0; rx_baud_count <= 0; rx_shift <= 0;
            end else if (rx_active) begin
                if (rx_baud_count == BAUD_DIV - 1) begin
                    rx_baud_count <= 0;
                    rx_bit_index <= rx_bit_index + 1'b1;
                    if (rx_bit_index < 8) rx_shift[rx_bit_index] <= uart_rx;
                    else begin
                        rx_active <= 0;
                        if (uart_rx) begin
                            if (!rx_full) begin rx_fifo[rx_wr_ptr] <= rx_shift; rx_wr_ptr <= (rx_wr_ptr == FIFO_DEPTH - 1) ? 0 : rx_wr_ptr + 1'b1; rx_count <= rx_count + 1'b1; end
                            else rx_overrun <= 1;
                        end else framing_error <= 1;
                    end
                end else rx_baud_count <= rx_baud_count + 1'b1;
            end
        end
    end

    // Basic protocol invariants intended for simulation-time checking.
    // synthesis translate_off
    always @(posedge pclk) begin
        if (presetn) begin
            assert (tx_count <= FIFO_DEPTH) else $error("TX FIFO count exceeded depth");
            assert (rx_count <= FIFO_DEPTH) else $error("RX FIFO count exceeded depth");
            assert (uart_tx === 1'b0 || uart_tx === 1'b1) else $error("UART TX became unknown");
        end
    end
    // synthesis translate_on
endmodule
