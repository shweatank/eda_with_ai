module multiplier(
	input wire[3:0] a,
	input wire[3:0] b,
	output wire[7:0] res
);
assign res =a*b;

initial begin
	$dumpfile("multiplier.vcd");
	$dumpvars(0,multiplier);
	end

endmodule

