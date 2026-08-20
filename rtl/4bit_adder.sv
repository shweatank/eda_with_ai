module full_adder(
	input logic a,
	input logic b,
	input logic cin,
	output logic sum,
	output logic cout
);
always_comb begin
	cout=(a&b)+(b&cin)+(a&cin);
	sum=a^b^cin;
	end
endmodule

module four_bit_adder(
	input logic[3:0] a,
	input logic[3:0] b,
	input logic cin,
	output logic[3:0]sum,
	output logic cout
);
	logic[4:0] carry;
	assign carry[0]=cin;
	assign cout=carry[4];
	
	genvar i;
	generate 
		for (i=0;i<4;i++) begin :fa_gen
			full_adder fa(
				.a(a[i]),
				.b(b[i]),
				.cin(carry[i]),
				.sum(sum[i]),
				.cout(carry[i+1])
			);
		end
	endgenerate
	
initial begin
	$dumpfile("four_bit_adder.vcd");
	$dumpvars(0,four_bit_adder);
	end
endmodule


