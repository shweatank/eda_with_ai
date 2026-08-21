from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

import cocotb
from cocotb.triggers import Timer


RESULT_PATTERN = re.compile(r"RESULT\s+(\d+)\s+(\d+)\s+(\d+)")
RTL_FILE = Path(__file__).with_name("comparator.sv")


def run_comparator_simulation(a: int, b: int) -> tuple[int, int, int]:
    """Run one pair of values through the comparator RTL."""
    testbench = f"""
module comparator_request_tb;
    reg [7:0] a;
    reg [7:0] b;
    wire equal;
    wire greater;
    wire less;

    comparator dut (
        .a(a), .b(b), .equal(equal), .greater(greater), .less(less)
    );

    initial begin
        a = {a};
        b = {b};
        #1;
        $display("RESULT %0d %0d %0d", equal, greater, less);
        $finish;
    end
endmodule
"""

    with tempfile.TemporaryDirectory(prefix="comparator_sim_") as temp_dir:
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
    return tuple(int(value) for value in match.groups())


@cocotb.test()
async def test_comparator(dut):
    cases = [
        (0, 0),
        (1, 0),
        (0, 1),
        (255, 255),
        (255, 254),
        (0, 255),
        (42, 42),
        (128, 127),
    ]

    for a, b in cases:
        dut.a.value = a
        dut.b.value = b
        await Timer(1, unit="ns")

        got_equal = int(dut.equal.value)
        got_greater = int(dut.greater.value)
        got_less = int(dut.less.value)

        expected_equal = int(a == b)
        expected_greater = int(a > b)
        expected_less = int(a < b)

        print(
            f"PASS: a={a}, b={b} -> equal={got_equal}, "
            f"greater={got_greater}, less={got_less}"
        )

        assert got_equal == expected_equal
        assert got_greater == expected_greater
        assert got_less == expected_less
