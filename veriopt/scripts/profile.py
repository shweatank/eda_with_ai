import sys, re, json, subprocess, sqlite3

def analyze_outputs(netlist, vcd, sta_report):
    with open(netlist) as f: net = f.read()
    cells = len(re.findall(r"\$[a-zA-Z]+", net))
    ff = len(re.findall(r"DFF", net))
    mux = len(re.findall(r"MUX", net))

    with open(sta_report) as f: sta = f.read()
    critical_path = re.search(r"Critical Path:\s+(\d+\.?\d*)", sta)
    delay = float(critical_path.group(1)) if critical_path else 0.0

    suggestions = []
    if mux > 10: suggestions.append("reduce muxes")
    if ff > 20: suggestions.append("reduce flipflops")
    if cells > 100: suggestions.append("simplify logic")
    if delay > 10: suggestions.append("pipeline critical path")

    return {"cells": cells, "flipflops": ff, "muxes": mux, "delay": delay, "suggestions": suggestions}

def log_design(name, file_path, status, suggestions=""):
    conn = sqlite3.connect("veriopt.db")
    c = conn.cursor()
    c.execute("INSERT INTO designs (name, file_path, status, suggestions) VALUES (?,?,?,?)",
              (name, file_path, status, suggestions))
    conn.commit()
    conn.close()

def main(netlist, vcd, sta_report):
    report = analyze_outputs(netlist, vcd, sta_report)
    with open("results/profile_report.html","w") as f:
        f.write("<h1>Optimization Report</h1><pre>"+json.dumps(report, indent=4)+"</pre>")
    print("Optimization report:", report)

    log_design("uploaded_design", netlist, "profiled", ", ".join(report["suggestions"]))

    if report["suggestions"]:
        prompt = "Optimize RTL: " + ", ".join(report["suggestions"])
        subprocess.run(["ollama", "run", "llama2:7b", "--prompt", prompt])

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
