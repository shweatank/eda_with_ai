`timescale 1ns/1ps

// ============================================================
// PARAMETERIZED COUNTER
// ============================================================

module counter #(
    parameter WIDTH = 8
)(
    input  wire             clk,
    input  wire             reset,
    output reg [WIDTH-1:0]  count
);


    // ========================================================
    // COUNTER LOGIC
    // ========================================================

    always @(posedge clk or posedge reset) begin

        // ----------------------------------------------------
        // ASYNCHRONOUS RESET
        // ----------------------------------------------------

        if (reset)

            count <= {WIDTH{1'b0}};


        // ----------------------------------------------------
        // COUNT INCREMENT
        // ----------------------------------------------------

        else

            count <= count + 1'b1;

    end


    // ========================================================
    // WAVEFORM DUMP
    // ========================================================

`ifdef COCOTB_SIM

    initial begin

        $dumpfile("waves/rtl.vcd");

        $dumpvars(0, counter);

    end

`endif

endmodule