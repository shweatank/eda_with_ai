import subprocess
import os

def run_cmd(command):
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout: print(result.stdout)
    if result.stderr: print(result.stderr)
    return result.returncode

if __name__ == "__main__":
    print("=== Compiling & Simulating Combinational Circuits ===")
    
    if run_cmd("iverilog -g2012 -o sim.out combinational_blocks.sv") != 0:
        print("Compilation failed!")
        exit(1)

    if run_cmd("vvp sim.out") != 0:
        print("Simulation failed!")
        exit(1)

    print("=== Simulation Passed Successfully! ===")
