from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

import cocotb
from cocotb.triggers import Timer


RESULT_PATTERN = re.compile(r"RESULT\s+(\d+)\s+(-?\d+)")
RTL_FILE = Path(__file__).with_name("arithmetic.sv")


def run_arithmetic_simulation(values: dict[str, int]) -> tuple[int, int]:
    """Run one request through the arithmetic RTL and return both results."""
    testbench = f"""
module arithmetic_request_tb;
    reg [7:0] a_u;
    reg [7:0] b_u;
    reg signed [7:0] a_s;
    reg signed [7:0] b_s;
    reg [2:0] op;
    wire [15:0] u_result;
    wire signed [15:0] s_result;

    arithmetic_all dut (
        .a_u(a_u), .b_u(b_u), .a_s(a_s), .b_s(b_s), .op(op),
        .u_result(u_result), .s_result(s_result)
    );

    initial begin
        a_u = {values['a_u']};
        b_u = {values['b_u']};
        a_s = {values['a_s']};
        b_s = {values['b_s']};
        op = {values['op']};
        #1;
        $display("RESULT %0d %0d", u_result, s_result);
        $finish;
    end
endmodule
"""

    with tempfile.TemporaryDirectory(prefix="arithmetic_sim_") as temp_dir:
        temp_path = Path(temp_dir)
        testbench_file = temp_path / "request_tb.sv"
        output_file = temp_path / "request_sim.vvp"
        testbench_file.write_text(testbench)

        compile_result = subprocess.run(
            ["iverilog", "-g2012", "-o", str(output_file), str(RTL_FILE), str(testbench_file)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if compile_result.returncode != 0:
            raise RuntimeError(compile_result.stderr.strip() or "RTL compilation failed")

        simulation_result = subprocess.run(
            ["vvp", str(output_file)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if simulation_result.returncode != 0:
            raise RuntimeError(simulation_result.stderr.strip() or "RTL simulation failed")

    match = RESULT_PATTERN.search(simulation_result.stdout)
    if match is None:
        raise RuntimeError("simulation result not found")
    return int(match.group(1)), int(match.group(2))


@cocotb.test()
async def test_arithmetic_select(dut):
    cases = [
        # op, a_u, b_u, a_s, b_s, expected_u, expected_s
        (0, 12, 5, -12, 5, 17, -7),      # sum
        (1, 12, 5, -12, 5, 7, -17),     # subtract
        (2, 12, 5, -12, 5, 60, -60),    # multiply
        (3, 12, 5, -12, 5, 2, -2),      # divide
        (4, 12, 5, -12, 5, 2, -2),      # remainder
        (3, 12, 0, -12, 0, 0, 0),       # divide by zero -> 0
        (4, 12, 0, -12, 0, 12, -12),    # remainder by zero -> a
        (0, 20, 3, -20, -3, 23, -23),   # signed negative + negative
        (1, 20, 3, -20, -3, 17, -17),   # signed negative - negative
        (2, 20, 3, -20, -3, 60, 60),    # signed negative * negative
        (3, 20, 3, -20, -3, 6, 6),      # divide
        (4, 20, 3, -20, -3, 2, -2),     # remainder
        (0, 20, 3, -20, 3, 23, -17),    # mixed sign sum
        (1, 20, 3, -20, 3, 17, -23),   # mixed sign subtract
        (2, 20, 3, -20, 3, 60, -60),   # mixed sign multiply
        (3, 20, 3, -20, 3, 6, -6),     # mixed sign divide
        (4, 20, 3, -20, 3, 2, -2),     # mixed sign remainder
    ]

    for op, a_u, b_u, a_s, b_s, exp_u, exp_s in cases:
        dut.a_u.value = a_u
        dut.b_u.value = b_u
        dut.a_s.value = a_s
        dut.b_s.value = b_s
        dut.op.value = op

        await Timer(1, unit="ns")

        got_u = int(dut.u_result.value)
        got_s = int(dut.s_result.value.to_signed())

        assert got_u == exp_u, (
            f"FAIL unsigned op={op}: {a_u} op {b_u} = {got_u}, expected {exp_u}"
        )
        assert got_s == exp_s, (
            f"FAIL signed op={op}: {a_s} op {b_s} = {got_s}, expected {exp_s}"
        )

        print(
            f"PASS op={op}: unsigned={got_u}, signed={got_s}"
        )
