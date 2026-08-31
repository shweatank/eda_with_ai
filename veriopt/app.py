from flask import Flask, request, jsonify
from graphql import build_schema, graphql_sync
from neo4j import GraphDatabase
import subprocess, os, re

app = Flask(__name__)

# Connect to Neo4j
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

# GraphQL schema
schema = build_schema("""
    type Design {
        id: ID!
        name: String!
        filePath: String!
        status: String!
        suggestions: String
    }

    type Query {
        designs: [Design!]!
        design(name: String!): Design
    }

    type Mutation {
        generateDesign(name: String!): Design
        generateTestbench(tbType: String!): Design
        simulate: Design
        synthesize: Design
        analyzeGds: Design
    }
""")

# -------------------------------
# Helper functions
# -------------------------------
def generate_code(prompt, filepath):
    """Call Ollama to generate code and save to file."""
    result = subprocess.run(["ollama", "run", "llama2:7b", prompt],
                            capture_output=True, text=True)
    code = result.stdout
    match = re.search(r"```(?:systemverilog|verilog|python)?\n(.*?)```", code, re.DOTALL)
    if match:
        code = match.group(1)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(code)
    return filepath

def log_design(name, file_path, status, suggestions=""):
    """Log design node into Neo4j."""
    with driver.session() as session:
        session.run("""
            MERGE (d:Design {name:$name})
            SET d.filePath=$file_path, d.status=$status, d.suggestions=$suggestions
        """, name=name, file_path=file_path, status=status, suggestions=suggestions)

# -------------------------------
# Resolvers
# -------------------------------
def resolve_designs(obj, info):
    with driver.session() as session:
        result = session.run("MATCH (d:Design) RETURN d")
        return [
            {
                "id": str(r["d"].id),
                "name": r["d"]["name"],
                "filePath": r["d"]["filePath"],
                "status": r["d"]["status"],
                "suggestions": r["d"].get("suggestions", "")
            }
            for r in result
        ]

def resolve_design(obj, info, name):
    with driver.session() as session:
        result = session.run("MATCH (d:Design {name:$name}) RETURN d", name=name)
        record = result.single()
        if record:
            d = record["d"]
            return {
                "id": str(d.id),
                "name": d["name"],
                "filePath": d["filePath"],
                "status": d["status"],
                "suggestions": d.get("suggestions", "")
            }
        return None

def resolve_generate_design(obj, info, name):
    filepath = generate_code(
        f"Output ONLY valid SystemVerilog RTL code for {name}. Include synthesizable logic.",
        f"src/{name.lower()}.sv"
    )
    log_design(name, filepath, "rtl_generated")
    return {"id": "1", "name": name, "filePath": filepath, "status": "rtl_generated"}

def resolve_generate_testbench(obj, info, tbType):
    filepath = generate_code(
        "Output ONLY Python Cocotb testbench code. The file must start with 'import cocotb'.",
        "tb/test.py"
    )
    log_design("latest_design", filepath, "tb_generated")
    return {"id": "2", "name": "testbench", "filePath": filepath, "status": "tb_generated"}

def resolve_simulate(obj, info):
    subprocess.run("make sim", shell=True)
    log_design("latest_design", "results/design.vcd", "simulated")
    return {"id": "3", "name": "latest_design", "filePath": "results/design.vcd", "status": "simulated"}

def resolve_synthesize(obj, info):
    subprocess.run("make synth", shell=True)
    log_design("latest_design", "results/netlist.v", "synthesized")
    return {"id": "4", "name": "latest_design", "filePath": "results/netlist.v", "status": "synthesized"}

def resolve_analyze_gds(obj, info):
    filepath = "results/final_report.txt"
    generate_code(
        "Analyze RTL, testbench, simulation VCD, synthesis, STA, PD, DRC/LVS, and GDSII. Output ONLY plain text summary verdict.",
        filepath
    )
    log_design("latest_design", filepath, "ai_report")
    return {"id": "5", "name": "latest_design", "filePath": filepath, "status": "ai_report", "suggestions": "See final report"}

# -------------------------------
# Root binding
# -------------------------------
root = {
    "designs": resolve_designs,
    "design": resolve_design,
    "generateDesign": resolve_generate_design,
    "generateTestbench": resolve_generate_testbench,
    "simulate": resolve_simulate,
    "synthesize": resolve_synthesize,
    "analyzeGds": resolve_analyze_gds,
}

# -------------------------------
# Flask routes
# -------------------------------
@app.route("/", methods=["GET"])
def index():
    return "GraphQL server is running. Send POST requests to /graphql"

@app.route("/graphql", methods=["GET", "POST"])
def graphql_server():
    if request.method == "GET":
        return "Send GraphQL queries as POST JSON to this endpoint."
    data = request.get_json()
    success, result = graphql_sync(schema, data.get("query"), root_value=root)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
