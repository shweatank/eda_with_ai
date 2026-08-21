from fastapi import FastAPI
import subprocess

app = FastAPI()


@app.post("/run-comparator")
def run_comparator():

    result = subprocess.run(
        ["make", "-f", "comparator.mk"],
        cwd="../MAKE_FILES",
        capture_output=True,
        text=True
    )

    return {
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }
