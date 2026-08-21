import subprocess
import os

def run_cmd(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout: print(result.stdout)
    return result.returncode

if __name__ == "__main__":
    if run_cmd("iverilog -g2012 -o sim.out mux4.sv") == 0:
        run_cmd("vvp sim.out")
