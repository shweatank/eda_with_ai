# File: files_alu_flask/app.py
from flask import Flask, jsonify, render_template_string, Response
import subprocess
import os
from groq import Groq

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ALU + Groq Streaming Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        pre { background: #eee; padding: 10px; border-radius: 4px; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <h1>Hardware ALU + Groq Streaming AI</h1>
    <div class="card">
        <h3>Run Simulation & Stream AI Analysis</h3>
        <button onclick="runSimulation()">Trigger ALU Simulation</button>
        <p id="status" style="font-weight: bold; color: green;"></p>
    </div>
    
    <div class="card">
        <h3>Hardware Results</h3>
        <pre id="hardware-data">Click the button above to run...</pre>
    </div>

    <div class="card">
        <h3>Groq AI Streaming Engineering Explanation</h3>
        <p id="ai-explanation" style="line-height: 1.6; white-space: pre-wrap;">Waiting for data...</p>
    </div>

    <script>
        async function runSimulation() {
            document.getElementById('status').innerText = "Running simulation...";
            document.getElementById('ai-explanation').innerText = "";
            
            // 1. Fetch hardware metrics first
            const res = await fetch('/simulate');
            const data = await res.json();
            document.getElementById('hardware-data').innerText = JSON.stringify(data.hardware_metrics, null, 2);
            
            document.getElementById('status').innerText = "Streaming Groq AI analysis...";
            
            // 2. Open EventSource to stream the AI response word by word
            const eventSource = new EventSource('/stream-ai');
            eventSource.onmessage = function(event) {
                if (event.data === "[DONE]") {
                    eventSource.close();
                    document.getElementById('status').innerText = "Complete!";
                } else {
                    document.getElementById('ai-explanation').innerText += event.data;
                }
            };
            eventSource.onerror = function() {
                eventSource.close();
                document.getElementById('status').innerText = "Stream finished or closed.";
            };
        }
    </script>
</body>
</html>
"""

# Global storage to hold metrics between requests
latest_metrics = {}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/simulate', methods=['GET'])
def simulate_hardware():
    global latest_metrics
    subprocess.run("iverilog -g2012 -o sim.out alu.sv", shell=True)
    result = subprocess.run("vvp sim.out", shell=True, capture_output=True, text=True)
    
    sim_data = ""
    for line in result.stdout.splitlines():
        if line.startswith("VALS:"):
            sim_data = line.replace("VALS:", "").strip()

    if not sim_data:
        return jsonify({"error": "Failed to capture simulation data"}), 500

    vals = sim_data.split(",")
    latest_metrics = {
        "operand_a": vals[0],
        "operand_b": vals[1],
        "cin": vals[2],
        "is_signed": vals[3],
        "opcode": vals[4],
        "result": vals[5],
        "cout_bout": vals[6],
        "overflow": vals[7],
            "div_by_zero": vals[8]
    }

    return jsonify({"hardware_metrics": latest_metrics})

@app.route('/stream-ai', methods=['GET'])
def stream_ai():
    def generate():
        try:
            client = Groq()
            prompt = f"""
            I simulated a 4-bit hardware ALU.
            Inputs: a={latest_metrics.get('operand_a', '0000')}, b={latest_metrics.get('operand_b', '0000')} (binary)
            Operation: Signed Addition
            Result: {latest_metrics.get('result', '0000')}
            Overflow Flag: {latest_metrics.get('overflow', '0')} (1=True, 0=False)
            Explain briefly why the overflow flag triggered based on Two's complement arithmetic.
            """
            
            # Enable streaming response from Groq
            stream = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-20b",
                stream=True
            )
            
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    # Format as Server-Sent Events (SSE) data stream
                    yield f"data: {content}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: Groq API Error: {str(e)}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
