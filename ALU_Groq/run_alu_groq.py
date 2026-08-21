# File: files_alu_groq/run_alu_groq.py
import subprocess
import os
from groq import Groq

def run_cmd(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

if __name__ == "__main__":
    print("=== Step 1: Running Hardware Simulation (Verilog) ==  ")
    
    # Clean and compile
    os.system("iverilog -g2012 -o sim.out alu.sv")
    sim_output = run_cmd("vvp sim.out")
    print(sim_output)

    # Extract simulation result line starting with VALS:
    sim_data = ""
    for line in sim_output.splitlines():
        if line.startswith("VALS:"):
            sim_data = line.replace("VALS:", "").strip()

    if not sim_data:
        print("Error capturing simulation data.")
        exit(1)

    print(f"Captured Hardware Data: {sim_data}")

    # Parse simulation results (a, b, cin, is_signed, opcode, result, cout_bout, overflow, div_by_zero)
    vals = sim_data.split(",")
    a, b, res, overflow = vals[0], vals[1], vals[5], vals[7]

    print("\n=== Step 2: Sending Hardware Data to Groq AI ===")
    
    # Initialize Groq Client (pulls GROQ_API_KEY from environment variables)
    client = Groq()

    prompt = f"""
    I just simulated a 4-bit hardware ALU in Verilog. 
    Inputs: a = {a}, b = {b} (Both binary)
    Operation: Signed Addition
    Hardware Simulation Output Result: {res}
    Hardware Overflow Flag Triggered: {overflow} (1 = True, 0 = False)

    As an expert hardware engineer, please explain in 2 short sentences why the overflow flag was triggered for these specific binary values in Two's Complement arithmetic.
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an expert digital hardware and computer architecture assistant."},
            {"role": "user", "content": prompt}
        ],
        model="openai/gpt-oss-20b",  # Fast, lightweight model on Groq
    )

    print("\n--- Groq AI Engineering Analysis ---")
    print(chat_completion.choices[0].message.content)
    print("--------------------------------------")