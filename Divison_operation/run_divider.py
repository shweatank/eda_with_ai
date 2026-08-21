# File: files_divider/run_divider.py
import subprocess
import os

def run_cmd(command):
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode

if __name__ == "__main__":
    print("=== Python Test Runner for Divider ===")
    
    for f in ["sim.out", "divider.vcd", "synth_netlist.v", "netlist.png", "netlist.dot"]:
        if os.path.exists(f):
            os.remove(f)

    if run_cmd("iverilog -g2012 -o sim.out divider.sv") != 0:
        print("Compilation failed!")
        exit(1)

    if run_cmd("vvp sim.out") != 0:
        print("Simulation failed!")
        exit(1)

    print("=== Simulation completed successfully! waveform generated (divider.vcd) ===")
