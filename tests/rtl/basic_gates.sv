
module and_gate (
    input  wire a,
    input  wire b,
    output wire y
);

    assign y = a & b;
    initial begin
	$dumpfile("and_gate.vcd");
	$dumpvars(0,and_gate);
	end


endmodule


module or_gate (
    input  wire a,
    input  wire b,
    output wire y
);

    assign y = a | b;
    initial begin
	$dumpfile("or_gate.vcd");
	$dumpvars(0,or_gate);
	end


endmodule

module nand_gate (
    input  wire a,
    input  wire b,
    output wire y
);

    assign y = ~(a & b);
    initial begin
	$dumpfile("nand_gate.vcd");
	$dumpvars(0,nand_gate);
	end


endmodule

module nor_gate (
    input  wire a,
    input  wire b,
    output wire y
);

    assign y = ~(a | b);
    initial begin
	$dumpfile("nor_gate.vcd");
	$dumpvars(0,nor_gate);
	end


endmodule

module not_gate (
    input  wire a,
    output wire y
);

    assign y = ~a;
    initial begin
	$dumpfile("not_gate.vcd");
	$dumpvars(0,not_gate);
	end




endmodule

