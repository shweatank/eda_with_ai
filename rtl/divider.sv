module divider(
	input wire[3:0] a,
	input wire[3:0] b,
	output wire[3:0] res
);
assign res = (b == 0) ? 4'b0000 : a / b;

initial begin
	$dumpfile("Divider.vcd");
	$dumpvars(0,divider);
	end

endmodule

