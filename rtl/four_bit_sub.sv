module four_bit_sub(
	input wire signed[3:0] a,
	input wire signed[3:0] b,
	input wire op,
	output wire signed[3:0]dif
);
assign dif=a-b;
initial begin
	$dumpfile("four_bit_sub.vcd");
	$dumpvars(0,four_bit_sub);
	end
endmodule



