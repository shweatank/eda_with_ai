from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

import cocotb
from cocotb.triggers import Timer


RESULT_PATTERN = re.compile(r"RESULT\s+(\d+)")
RTL_FILE = Path(__file__).with_name("decoder.sv")


def run_decoder_simulation(a: int) -> int:
    """Run one input value through the decoder RTL."""
    testbench = f"""
module decoder_request_tb;
    reg [1:0] a;
    wire [3:0] y;

    decoder dut (
        .a(a),
        .y(y)
    );

    initial begin
        a = {a};
        #1;
        $display("RESULT %0d", y);
        $finish;
    end
endmodule
"""

    with tempfile.TemporaryDirectory(prefix="decoder_sim_") as temp_dir:
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
    return int(match.group(1))


@cocotb.test()
async def test_decoder_2to4(dut):
    expected_outputs = {
        0b00: 0b0001,
        0b01: 0b0010,
        0b10: 0b0100,
        0b11: 0b1000,
    }

    for a, expected in expected_outputs.items():
        dut.a.value = a
        await Timer(1, unit="ns")

        got = int(dut.y.value)
        print(f"PASS: a={a:02b} -> y={got:04b} (expected {expected:04b})")
        assert got == expected
