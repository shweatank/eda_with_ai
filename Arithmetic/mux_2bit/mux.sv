module mux_2bit (
	input wire a,
	input wire b,
	input wire sel,
	output wire y
);

	assign y = sel ? b : a;

endmodule
