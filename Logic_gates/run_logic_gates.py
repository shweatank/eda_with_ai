# File: files_logic_gates/run_logic_gates.py
import subprocess
import os

def run_cmd(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode

if __name__ == "__main__":
    print("=== Running Logic Gates Simulation ===")
    if run_cmd("iverilog -g2012 -o sim.out logic_gates.sv") == 0:
        run_cmd("vvp sim.out")
