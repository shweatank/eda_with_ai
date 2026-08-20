module four_bit_ALU(
	input wire signed[3:0] a,
	input wire signed[3:0] b,
	input wire op,
	output wire signed[3:0]sum
);
assign sum=a+b;
initial begin
	$dumpfile("four_bit_ALU.vcd");
	$dumpvars(0,four_bit_ALU);
	end
endmodule



