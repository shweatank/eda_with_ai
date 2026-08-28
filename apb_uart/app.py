from __future__ import annotations
import json, os, subprocess
from pathlib import Path
from urllib import request, error
from flask import Flask, jsonify, render_template, request as flask_request
app=Flask(__name__); PROJECT_DIR=Path(__file__).resolve().parent
ARTIFACTS={
    "waveform": PROJECT_DIR / "apb_uart.vcd",
    "netlist": PROJECT_DIR / "apb_uart_netlist.v",
    "diagram": PROJECT_DIR / "apb_uart.dot",
    "image": PROJECT_DIR / "apb_uart.png",
}; MEMORY=[]
def run_make(target="",width=8,depth=4):
    subprocess.run(["make","clean_apb_uart"],cwd=PROJECT_DIR,capture_output=True,text=True,check=False)
    command=["make",f"DATA_WIDTH={width}",f"FIFO_DEPTH={depth}"]+([target] if target else [])
    result=subprocess.run(command,cwd=PROJECT_DIR,capture_output=True,text=True,timeout=120,check=False)
    return result.returncode==0,(result.stdout+result.stderr).strip()[-4000:]
def evidence():
    source=(PROJECT_DIR/"apb_uart.sv").read_text(); netlist=ARTIFACTS["netlist"].read_text() if ARTIFACTS["netlist"].is_file() else ""
    checks=[f"RTL missing: {x}" for x in ["psel","penable","uart_rx","uart_tx","irq","assert"] if x not in source]+[f"netlist missing: {x}" for x in ["module apb_uart(","prdata","pready","pslverr"] if x not in netlist]
    return {"artifact_files":{k:p.is_file() for k,p in ARTIFACTS.items()},"checks":checks}
def ollama(data):
    model=os.getenv("OLLAMA_MODEL","llama3.2:latest"); payload={"model":model,"prompt":"Review APB UART evidence. Return exactly {\"verdict\":\"PASS\"} or {\"verdict\":\"FAIL\"}.\n"+json.dumps(data),"stream":False,"format":"json"}
    try:
        req=request.Request(os.getenv("OLLAMA_URL","http://127.0.0.1:11434/api/generate"),data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"},method="POST")
        with request.urlopen(req,timeout=15) as response: verdict=json.loads(json.loads(response.read().decode())["response"])["verdict"]
        return {"source":f"ollama:{model}","verdict":verdict,"summary":"Ollama review completed."}
    except (OSError,ValueError,KeyError,json.JSONDecodeError,error.URLError) as exc: return {"source":"ollama-unavailable","verdict":"FAIL","summary":str(exc)}
@app.get("/")
def index(): return render_template("index.html")
@app.get("/health")
def health(): return jsonify(status="ok")
@app.post("/api/operate")
def operate():
    data=flask_request.get_json(silent=True) or {}; operation=data.get("operation","status"); width=int(data.get("data_width",8)); depth=int(data.get("fifo_depth",4)); value=int(str(data.get("value","0")),0)&((1<<width)-1)
    if width not in {8,16,32,64} or depth not in {4,8,16,32,64}: return jsonify(error="choose valid data width and FIFO depth"),400
    if operation=="reset": MEMORY.clear()
    elif operation=="write":
        if len(MEMORY)>=depth:return jsonify(error="FIFO full",count=len(MEMORY),full=True),409
        MEMORY.append(value)
    elif operation=="read":
        if not MEMORY:return jsonify(error="FIFO empty",count=0,empty=True),409
        value=MEMORY.pop(0)
    return jsonify(operation=operation,data_width=width,fifo_depth=depth,count=len(MEMORY),full=len(MEMORY)>=depth,empty=not MEMORY,value=f"0x{value:0{width//4}X}",binary=f"{value:0{width}b}",queue=[f"0x{x:0{width//4}X}" for x in MEMORY])
@app.post("/api/verify")
def verify():
    configs=(flask_request.get_json(silent=True) or {}).get("configurations",[{"data_width":8,"fifo_depth":4},{"data_width":16,"fifo_depth":8},{"data_width":32,"fifo_depth":16}]); results=[]
    for config in configs:
        width,depth=int(config["data_width"]),int(config["fifo_depth"]); passed,output=run_make(width=width,depth=depth); results.append({"data_width":width,"fifo_depth":depth,"status":"PASS" if passed else "FAIL","output":output})
    artifacts_ok,artifact_output=run_make("artifacts"); data=evidence(); netlist_ok=not data["checks"]; local_ok=all(x["status"]=="PASS" for x in results) and artifacts_ok and all(data["artifact_files"].values()) and netlist_ok; data["configurations"]=results
    return jsonify(status="PASS" if local_ok else "FAIL",local={"functional_test":"PASS" if all(x["status"]=="PASS" for x in results) else "FAIL","artifact_generation":"PASS" if artifacts_ok else "FAIL","netlist_check":"PASS" if netlist_ok else "FAIL","configurations":results,"details":data["checks"],"test_output":"\n\n".join(x["output"] for x in results),"artifact_output":artifact_output},ai=ollama(data))
if __name__=="__main__": app.run(host="127.0.0.1",port=int(os.getenv("PORT","5010")),debug=False)
