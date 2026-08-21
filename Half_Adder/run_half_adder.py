# File: files_half_adder/run_half_adder.py
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
    print("=== Python Test Runner for Half Adder ===")
    
    for f in ["sim.out", "half_adder.vcd", "synth_netlist.v", "netlist.png", "netlist.dot"]:
        if os.path.exists(f):
            os.remove(f)

    if run_cmd("iverilog -g2012 -o sim.out half_adder.sv") != 0:
        print("Compilation failed!")
        exit(1)

    if run_cmd("vvp sim.out") != 0:
        print("Simulation failed!")
        exit(1)

    print("=== Simulation completed successfully! Waveform generated (half_adder.vcd) ===")
