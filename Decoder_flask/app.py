from flask import Flask, jsonify, render_template_string, Response
import subprocess
import os
from groq import Groq

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>2-to-4 Decoder + Groq AI</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        pre { background: #eee; padding: 10px; border-radius: 4px; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <h1>2-to-4 Decoder + Groq AI</h1>
    <div class="card">
        <h3>Run Hardware Simulation & Stream AI</h3>
        <button onclick="runSimulation()">Simulate Decoder</button>
        <p id="status" style="font-weight: bold; color: green;"></p>
    </div>
    
    <div class="card">
        <h3>Hardware Metrics</h3>
        <pre id="hardware-data">Click button above...</pre>
    </div>

    <div class="card">
        <h3>Groq AI Engineering Explanation</h3>
        <p id="ai-explanation" style="line-height: 1.6; white-space: pre-wrap;">Waiting for simulation...</p>
    </div>

    <script>
        async function runSimulation() {
            document.getElementById('status').innerText = "Running Verilog simulation...";
            document.getElementById('ai-explanation').innerText = "";
            
            const res = await fetch('/simulate');
            const data = await res.json();
            
            document.getElementById('hardware-data').innerText = JSON.stringify(data.hardware_metrics, null, 2);
            document.getElementById('status').innerText = "Streaming Groq response...";
            
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
                document.getElementById('status').innerText = "Stream finished.";
            };
        }
    </script>
</body>
</html>
"""

latest_metrics = {}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/simulate', methods=['GET'])
def simulate():
    global latest_metrics
    subprocess.run("iverilog -g2012 -o sim.out decoder.sv", shell=True)
    result = subprocess.run("vvp sim.out", shell=True, capture_output=True, text=True)
    
    sim_vals = []
    for line in result.stdout.splitlines():
        if line.startswith("RESULT:"):
            sim_vals = line.replace("RESULT:", "").strip().split(",")

    if not sim_vals:
        return jsonify({"error": "Simulation failed"}), 500

    latest_metrics = {
        "input_a": sim_vals[0],
        "output_y": sim_vals[1]
    }

    return jsonify({"hardware_metrics": latest_metrics})

@app.route('/stream-ai', methods=['GET'])
def stream_ai():
    def generate():
        try:
            client = Groq()
            prompt = f"""
            I simulated a 2-to-4 Decoder in Verilog.
            Binary Input: {latest_metrics.get('input_a')}
            Decoded One-Hot Output: {latest_metrics.get('output_y')}
            Explain briefly how this combinational circuit translates a 2-bit binary code into one of 4 mutually exclusive output lines.
            """
            
            stream = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-120b",
                stream=True
            )
            
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield f"data: {content}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: Groq API Error: {str(e)}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
