module logic_model(input a, input b, input c, output y);
    assign y = (a & b) | c;
    initial begin
        $dumpfile("dump_logic.vcd");
        $dumpvars(0, logic_model);
    end
endmodule