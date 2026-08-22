from fastapi import FastAPI
from pydantic import BaseModel
import subprocess

app=FastAPI()
class request(BaseModel):
    module:str
    enabled:bool
    
@app.get("/")
def greeting():
    return {"fine good starting"}
  
@app.post("/run-decoder")
def decoder_module(data:request):
    makefile=f"{data.module}.mk"
    result=subprocess.run(
       ["make", "-f", f"MAKE_FILES/{makefile}"],
       cwd="..",
       capture_output=True,
       text=True   
    )
    return {
        "status": "success" if result.returncode == 0 else "failed",
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }
